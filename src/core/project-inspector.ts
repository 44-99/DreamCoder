import { readFile, readdir, realpath, stat } from "node:fs/promises";
import path from "node:path";

const IGNORED_DIRECTORIES = new Set([".git", "node_modules", "dist", "build", "coverage", ".next", ".cache"]);
const SOURCE_EXTENSIONS = new Set([".html", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"]);
const MAX_FILES = 4_000;

export interface ProjectInspection {
  root: string;
  packageManager: "npm" | "pnpm" | "yarn" | "bun" | "unknown";
  frameworks: string[];
  scripts: Record<string, string>;
  entryCandidates: string[];
  sourceFileCount: number;
  bridge: {
    detected: boolean;
    files: string[];
  };
  recommendations: string[];
}

export class ProjectBoundary {
  private constructor(readonly root: string) {}

  static async create(configuredRoot: string): Promise<ProjectBoundary> {
    const resolved = await realpath(path.resolve(configuredRoot));
    const info = await stat(resolved);
    if (!info.isDirectory()) throw new Error(`WEB2DKIT_ROOT is not a directory: ${resolved}`);
    return new ProjectBoundary(resolved);
  }

  async resolve(relativePath = "."): Promise<string> {
    if (path.isAbsolute(relativePath)) {
      throw new Error("Project paths must be relative to WEB2DKIT_ROOT.");
    }

    const candidate = path.resolve(this.root, relativePath);
    const relative = path.relative(this.root, candidate);
    if (relative.startsWith("..") || path.isAbsolute(relative)) {
      throw new Error("Project path escapes WEB2DKIT_ROOT.");
    }

    const resolvedCandidate = await realpath(candidate);
    const resolvedRelative = path.relative(this.root, resolvedCandidate);
    if (resolvedRelative.startsWith("..") || path.isAbsolute(resolvedRelative)) {
      throw new Error("Project path resolves outside WEB2DKIT_ROOT.");
    }
    return resolvedCandidate;
  }
}

async function walk(directory: string, root: string, files: string[]): Promise<void> {
  if (files.length >= MAX_FILES) return;
  const entries = await readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    if (files.length >= MAX_FILES) return;
    if (entry.isSymbolicLink()) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (!IGNORED_DIRECTORIES.has(entry.name)) await walk(absolute, root, files);
    } else if (entry.isFile()) {
      files.push(path.relative(root, absolute).split(path.sep).join("/"));
    }
  }
}

function detectPackageManager(files: string[], declared?: string): ProjectInspection["packageManager"] {
  if (files.includes("pnpm-lock.yaml")) return "pnpm";
  if (files.includes("yarn.lock")) return "yarn";
  if (files.includes("bun.lock") || files.includes("bun.lockb")) return "bun";
  if (files.includes("package-lock.json")) return "npm";
  const name = declared?.split("@", 1)[0];
  if (name === "npm" || name === "pnpm" || name === "yarn" || name === "bun") return name;
  return "unknown";
}

export async function inspectProject(root: string): Promise<ProjectInspection> {
  const files: string[] = [];
  await walk(root, root, files);

  let packageJson: {
    packageManager?: string;
    scripts?: Record<string, string>;
    dependencies?: Record<string, string>;
    devDependencies?: Record<string, string>;
  } = {};
  if (files.includes("package.json")) {
    packageJson = JSON.parse(await readFile(path.join(root, "package.json"), "utf8"));
  }

  const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
  const frameworkDependencies: Array<[string, string]> = [
    ["phaser", "Phaser"],
    ["pixi.js", "PixiJS"],
    ["kaboom", "Kaboom"],
    ["excalibur", "Excalibur"],
    ["react", "React"],
    ["vue", "Vue"],
    ["svelte", "Svelte"]
  ];
  const frameworks = frameworkDependencies
    .filter(([dependency]) => dependency in dependencies)
    .map(([, label]) => label);

  const sourceFiles = files.filter((file) => SOURCE_EXTENSIONS.has(path.extname(file).toLowerCase()));
  const bridgeFiles: string[] = [];
  for (const file of sourceFiles.slice(0, 1_000)) {
    try {
      const source = await readFile(path.join(root, file), "utf8");
      if (source.includes("__WEB2D_GAME__")) bridgeFiles.push(file);
    } catch {
      // Ignore unreadable source files and continue the bounded inspection.
    }
  }

  const entryPatterns = /(^|\/)(index|main|game|app)\.(html|js|jsx|ts|tsx)$/i;
  const entryCandidates = sourceFiles.filter((file) => entryPatterns.test(file)).slice(0, 20);
  const recommendations: string[] = [];
  if (!files.includes("package.json")) recommendations.push("Add package.json scripts so agents can start the game consistently.");
  if (bridgeFiles.length === 0) recommendations.push("Install the Web2DKit Game Bridge to expose structured state and deterministic reset.");
  if (!(packageJson.scripts?.test || packageJson.scripts?.["test:e2e"])) recommendations.push("Add a repeatable test script for saved gameplay scenarios.");

  return {
    root,
    packageManager: detectPackageManager(files, packageJson.packageManager),
    frameworks,
    scripts: packageJson.scripts ?? {},
    entryCandidates,
    sourceFileCount: sourceFiles.length,
    bridge: { detected: bridgeFiles.length > 0, files: bridgeFiles.slice(0, 20) },
    recommendations
  };
}
