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
    expect(mcp).toHaveProperty("mcpServers.web2dkit");
    expect(JSON.stringify({ codex, mcp })).not.toContain("FastAPI");
  });

  it("ships complete operational Skills", async () => {
    for (const name of ["build-web2d-game", "playtest-web2d-game", "debug-web2d-game"]) {
      const skill = await readFile(`skills/${name}/SKILL.md`, "utf8");
      expect(skill).toContain(`name: ${name}`);
      expect(skill).not.toContain("TODO");
      expect(skill).toContain("web2d_");
    }
  });
});
