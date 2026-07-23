import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { inspectProject, ProjectBoundary } from "../src/core/project-inspector.js";

const temporaryDirectories: string[] = [];

afterEach(async () => {
  await Promise.all(temporaryDirectories.splice(0).map((directory) => rm(directory, { recursive: true, force: true })));
});

describe("project inspection boundary", () => {
  it("detects a Web 2D stack and bridge without reading node_modules", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "web2dkit-inspect-"));
    temporaryDirectories.push(root);
    await writeFile(path.join(root, "package.json"), JSON.stringify({
      scripts: { dev: "vite", test: "vitest" },
      dependencies: { phaser: "^3.90.0" }
    }));
    await writeFile(path.join(root, "package-lock.json"), "{}");
    await mkdir(path.join(root, "src"));
    await writeFile(path.join(root, "src", "main.ts"), "window.__WEB2D_GAME__ = bridge;");

    const result = await inspectProject(root);
    expect(result.packageManager).toBe("npm");
    expect(result.frameworks).toContain("Phaser");
    expect(result.bridge.detected).toBe(true);
    expect(result.entryCandidates).toContain("src/main.ts");
  });

  it("rejects paths outside the configured project root", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "web2dkit-boundary-"));
    temporaryDirectories.push(root);
    const boundary = await ProjectBoundary.create(root);
    await expect(boundary.resolve("../outside")).rejects.toThrow("escapes WEB2DKIT_ROOT");
    await expect(boundary.resolve(path.resolve(root))).rejects.toThrow("must be relative");
  });
});
