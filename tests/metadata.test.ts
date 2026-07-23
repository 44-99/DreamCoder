import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";

const readJson = async (path: string): Promise<Record<string, unknown>> => JSON.parse(await readFile(path, "utf8"));

describe("plugin metadata", () => {
  it("keeps package and host manifests aligned", async () => {
    const packageJson = await readJson("package.json");
    const codex = await readJson(".codex-plugin/plugin.json");
    const claude = await readJson(".claude-plugin/plugin.json");
    const mcp = await readJson(".mcp.json");

    expect(packageJson.name).toBe("web2dkit");
    expect(codex.name).toBe("web2dkit");
    expect(claude.name).toBe("web2dkit");
    expect(codex.version).toBe(packageJson.version);
    expect(claude.version).toBe(packageJson.version);
    expect(codex.description).toBe(packageJson.description);
    expect(claude.description).toBe(packageJson.description);
    expect(mcp).toHaveProperty("mcpServers.web2dkit");
    expect(JSON.stringify({ codex, mcp })).not.toContain("FastAPI");
  });

  it("ships complete operational Skills", async () => {
    for (const name of [
      "design-web2d-game",
      "build-web2d-game",
      "playtest-web2d-game",
      "debug-web2d-game",
      "polish-web2d-game",
    ]) {
      const skill = await readFile(`skills/${name}/SKILL.md`, "utf8");
      expect(skill).toContain(`name: ${name}`);
      expect(skill).not.toContain("TODO");
      expect(skill).toContain("web2d_");

      const metadata = await readFile(`skills/${name}/agents/openai.yaml`, "utf8");
      expect(metadata).toContain(`$${name}`);
      expect(metadata).toContain('value: "web2dkit"');
    }
  });

  it("routes game-development details through focused references", async () => {
    const expectedReferences = [
      "skills/design-web2d-game/references/game-design-contract.md",
      "skills/build-web2d-game/references/stack-selection.md",
      "skills/build-web2d-game/references/game-production.md",
      "skills/playtest-web2d-game/references/visual-quality.md",
      "skills/polish-web2d-game/references/quality-lenses.md",
    ];

    for (const reference of expectedReferences) {
      expect(await readFile(reference, "utf8")).not.toHaveLength(0);
    }
  });
});
