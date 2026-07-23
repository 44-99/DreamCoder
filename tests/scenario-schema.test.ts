import { mkdtemp, mkdir, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { loadScenarioDocuments, ScenarioDocumentSchema } from "../src/scenarios/schema.js";

describe("versioned scenario documents", () => {
  it("accepts a strict v1 scenario with initial assertions", () => {
    expect(ScenarioDocumentSchema.parse({
      schemaVersion: "1",
      name: "start ready",
      seed: 42,
      initialAssertions: [{ path: "status", operator: "equals", expected: "ready" }],
      steps: []
    }).schemaVersion).toBe("1");
  });

  it("rejects unknown fields", () => {
    expect(() => ScenarioDocumentSchema.parse({
      schemaVersion: "1",
      name: "unsafe",
      steps: [],
      script: "doAnything()"
    })).toThrow();
  });

  it("loads scenario directories in stable filename order", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "web2dkit-scenarios-"));
    await mkdir(path.join(root, "nested"));
    const scenario = (name: string) => JSON.stringify({ schemaVersion: "1", name, steps: [] });
    await writeFile(path.join(root, "b.web2d.json"), scenario("b"));
    await writeFile(path.join(root, "nested", "a.web2d.json"), scenario("a"));
    const notes = path.join(root, "README.md");
    await writeFile(notes, "Scenario notes");

    const loaded = await loadScenarioDocuments([root]);
    const files = loaded.map((item) => item.file);
    expect(files).toEqual([...files].sort());
    expect(loaded).toHaveLength(2);
    await expect(loadScenarioDocuments([notes])).rejects.toThrow("must end with .web2d.json");
  });
});
