import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

let client: Client;
let transport: StdioClientTransport;

beforeAll(async () => {
  client = new Client({ name: "web2dkit-test-client", version: "0.1.0" });
  transport = new StdioClientTransport({
    command: process.execPath,
    args: ["--import", "tsx", "src/server.ts"],
    cwd: process.cwd(),
    env: { ...process.env, WEB2DKIT_ROOT: process.cwd() } as Record<string, string>,
    stderr: "pipe"
  });
  await client.connect(transport);
});

afterAll(async () => {
  await client.close();
});

describe("MCP stdio contract", () => {
  it("lists the bounded Web2DKit tool surface", async () => {
    const result = await client.listTools();
    expect(result.tools.map((tool) => tool.name)).toEqual([
      "web2d_project_inspect",
      "web2d_session_start",
      "web2d_session_stop",
      "web2d_observe",
      "web2d_act",
      "web2d_assert",
      "web2d_scenario_run",
      "web2d_quality_check"
    ]);
    expect(result.tools.every((tool) => tool.inputSchema.type === "object")).toBe(true);
    expect(result.tools.every((tool) => tool.outputSchema?.type === "object")).toBe(true);
  });

  it("returns structured content from a real tool call", async () => {
    const result = await client.callTool({ name: "web2d_project_inspect", arguments: { path: "." } });
    expect(result.isError).not.toBe(true);
    expect(result.structuredContent).toMatchObject({
      ok: true,
      data: { packageManager: "npm", bridge: { detected: true } }
    });
  });
});
