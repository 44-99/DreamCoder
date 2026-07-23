import { readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";
import { z } from "zod";
import type { GameScenario, ScenarioDocument } from "../types.js";

export const ActionSchema = z.union([
  z.object({
    kind: z.literal("key"),
    key: z.string().min(1),
    phase: z.enum(["press", "down", "up"]).optional(),
    durationMs: z.number().int().min(0).max(30_000).optional()
  }).strict(),
  z.object({
    kind: z.literal("pointer"),
    x: z.number().finite(),
    y: z.number().finite(),
    phase: z.enum(["click", "down", "up"]).optional(),
    button: z.enum(["left", "middle", "right"]).optional()
  }).strict(),
  z.object({
    kind: z.literal("wait"),
    durationMs: z.number().int().min(0).max(60_000).optional(),
    frames: z.number().int().min(1).max(3_600).optional()
  }).strict().refine((value) => value.durationMs !== undefined || value.frames !== undefined, {
    message: "wait requires durationMs or frames"
  }),
  z.object({
    kind: z.literal("bridge"),
    name: z.string().min(1),
    payload: z.unknown().optional()
  }).strict()
]);

export const AssertionSchema = z.object({
  path: z.string(),
  operator: z.enum([
    "equals", "notEquals", "greaterThan", "greaterThanOrEqual",
    "lessThan", "lessThanOrEqual", "includes", "exists"
  ]),
  expected: z.unknown().optional(),
  message: z.string().optional()
}).strict();

const ScenarioFields = {
  name: z.string().min(1),
  seed: z.number().int().min(0).max(0xffffffff).optional(),
  initialAssertions: z.array(AssertionSchema).max(100).optional(),
  steps: z.array(z.object({
    action: ActionSchema,
    assertions: z.array(AssertionSchema).max(100).optional()
  }).strict()).max(500),
  finalAssertions: z.array(AssertionSchema).max(100).optional()
};

export const GameScenarioSchema = z.object(ScenarioFields).strict();
export const ScenarioDocumentSchema = z.object({ schemaVersion: z.literal("1"), ...ScenarioFields }).strict();

export interface LoadedScenario {
  file: string;
  scenario: ScenarioDocument;
}

async function collectScenarioFiles(input: string): Promise<string[]> {
  const info = await stat(input);
  if (info.isFile()) {
    if (!input.endsWith(".web2d.json")) throw new Error(`Scenario files must end with .web2d.json: ${input}`);
    return [input];
  }
  if (!info.isDirectory()) throw new Error(`Scenario path is not a file or directory: ${input}`);
  const entries = await readdir(input, { withFileTypes: true });
  const nested = await Promise.all(entries
    .filter((entry) => !entry.isSymbolicLink()
      && (entry.isDirectory() || (entry.isFile() && entry.name.endsWith(".web2d.json"))))
    .map((entry) => collectScenarioFiles(path.join(input, entry.name))));
  return nested.flat();
}

export async function loadScenarioDocuments(inputs: string[]): Promise<LoadedScenario[]> {
  if (inputs.length === 0) throw new Error("At least one .web2d.json file or directory is required.");
  const groups = await Promise.all(inputs.map((input) => collectScenarioFiles(path.resolve(input))));
  const files = [...new Set(groups.flat())].sort();
  if (files.length === 0) throw new Error("No .web2d.json scenario files were found.");

  return Promise.all(files.map(async (file) => {
    let raw: unknown;
    try {
      raw = JSON.parse(await readFile(file, "utf8"));
    } catch (error) {
      throw new Error(`Cannot read scenario ${file}: ${error instanceof Error ? error.message : String(error)}`);
    }
    const parsed = ScenarioDocumentSchema.safeParse(raw);
    if (!parsed.success) throw new Error(`Invalid scenario ${file}: ${parsed.error.message}`);
    return { file, scenario: parsed.data as GameScenario & ScenarioDocument };
  }));
}
