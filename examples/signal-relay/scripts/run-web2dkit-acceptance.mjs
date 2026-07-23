import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createServer } from "vite";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const web2dkitRoot = process.env.WEB2DKIT_REPO
  ? path.resolve(process.env.WEB2DKIT_REPO)
  : path.resolve(projectRoot, "..", "..");
const executeFile = promisify(execFile);

const client = new Client({ name: "signal-relay-acceptance", version: "0.1.0" });
const transport = new StdioClientTransport({
  command: process.execPath,
  args: [path.join(web2dkitRoot, "dist", "server.js")],
  cwd: web2dkitRoot,
  env: { ...process.env, WEB2DKIT_ROOT: projectRoot },
  stderr: "pipe"
});

function dataOf(result, tool) {
  if (result.isError || result.structuredContent?.ok !== true) {
    throw new Error(`${tool} failed: ${JSON.stringify(result.structuredContent)}`);
  }
  return result.structuredContent.data;
}

async function call(tool, args) {
  return dataOf(await client.callTool({ name: tool, arguments: args }), tool);
}

let sessionId;
let gameServer;
try {
  gameServer = await createServer({
    root: projectRoot,
    logLevel: "error",
    server: { host: "127.0.0.1", port: 0, strictPort: false }
  });
  await gameServer.listen();
  const gameUrl = gameServer.resolvedUrls?.local[0];
  if (!gameUrl) throw new Error("Vite did not expose a local Signal Relay URL.");
  const scenarioDirectory = path.join(projectRoot, "web2dkit", "scenarios");
  const cliRun = await executeFile(process.execPath, [
    path.join(web2dkitRoot, "dist", "cli.js"), "run", "--url", gameUrl,
    "--reporter", "json", scenarioDirectory
  ], { cwd: projectRoot });
  const cliSuite = JSON.parse(cliRun.stdout);

  const schemaModuleUrl = pathToFileURL(path.join(web2dkitRoot, "dist", "scenarios", "schema.js")).href;
  const { loadScenarioDocuments } = await import(schemaModuleUrl);
  const documents = await loadScenarioDocuments([scenarioDirectory]);
  const scenario = (name) => {
    const document = documents.find((item) => item.scenario.name === name)?.scenario;
    if (!document) throw new Error(`Missing scenario: ${name}`);
    const { schemaVersion: _schemaVersion, ...value } = document;
    return value;
  };
  const winningScenario = scenario("restore all relays and transmit");
  const pauseScenario = scenario("pause gates movement and resume restores it");

  await client.connect(transport);
  const toolNames = (await client.listTools()).tools.map((tool) => tool.name);
  const requiredTools = [
    "web2d_project_inspect", "web2d_session_start", "web2d_session_stop", "web2d_observe",
    "web2d_act", "web2d_assert", "web2d_scenario_run", "web2d_quality_check"
  ];
  const missingTools = requiredTools.filter((tool) => !toolNames.includes(tool));
  if (missingTools.length) throw new Error(`Missing MCP tools: ${missingTools.join(", ")}`);
  const inspection = await call("web2d_project_inspect", { path: "." });
  const session = await call("web2d_session_start", { url: gameUrl, seed: 42, width: 1280, height: 800, headless: true });
  sessionId = session.sessionId;

  const initial = await call("web2d_observe", { sessionId });
  await call("web2d_act", {
    sessionId,
    actions: [
      { kind: "key", key: "Enter" },
      { kind: "key", key: "ArrowRight" }
    ]
  });
  const nativeInput = await call("web2d_assert", {
    sessionId,
    assertions: [
      { path: "lifecycle.status", operator: "equals", expected: "playing" },
      { path: "player.position.x", operator: "equals", expected: 1 },
      { path: "player.energy", operator: "equals", expected: 17 }
    ]
  });

  const winningRun1 = await call("web2d_scenario_run", { sessionId, scenario: winningScenario });
  const winningRun2 = await call("web2d_scenario_run", { sessionId, scenario: winningScenario });

  const pauseRun = await call("web2d_scenario_run", { sessionId, scenario: pauseScenario });
  const quality = await call("web2d_quality_check", { sessionId });
  const deterministicReplay = JSON.stringify(winningRun1.finalState) === JSON.stringify(winningRun2.finalState);
  const passed = initial.state.lifecycle.seed === 42
    && nativeInput.passed
    && winningRun1.passed
    && winningRun2.passed
    && deterministicReplay
    && pauseRun.passed
    && cliSuite.passed
    && quality.passed;

  if (!passed) {
    throw new Error(`Signal Relay acceptance failed: ${JSON.stringify({ nativeInput, winningRun1, winningRun2, pauseRun, quality })}`);
  }

  console.log(JSON.stringify({
    ok: true,
    tools: toolNames.length,
    inspectedSources: inspection.sourceFileCount,
    bridgeDetected: inspection.bridge.detected,
    seed: initial.state.lifecycle.seed,
    nativeInput: nativeInput.passed,
    deterministicReplay,
    winningScore: winningRun1.finalState.player.score,
    pauseScenario: pauseRun.passed,
    cliScenarioSuite: cliSuite.passed,
    qualityCheck: quality.passed
  }, null, 2));
} finally {
  if (sessionId) {
    await client.callTool({ name: "web2d_session_stop", arguments: { sessionId } }).catch(() => undefined);
  }
  await client.close();
  await gameServer?.close();
}
