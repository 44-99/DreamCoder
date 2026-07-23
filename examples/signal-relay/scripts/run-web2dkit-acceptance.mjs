import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createServer } from "vite";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const web2dkitRoot = process.env.WEB2DKIT_REPO
  ? path.resolve(process.env.WEB2DKIT_REPO)
  : path.resolve(projectRoot, "..", "..");

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

const moves = [
  "right", "down",
  "right", "right", "right", "right",
  "down", "down", "down", "down",
  "down", "left", "left", "left", "left", "left"
];

const winningScenario = {
  name: "restore all relays and transmit",
  seed: 42,
  steps: [
    { action: { kind: "bridge", name: "start" }, assertions: [{ path: "lifecycle.status", operator: "equals", expected: "playing" }] },
    ...moves.map((direction, index) => ({
      action: { kind: "bridge", name: "move", payload: { direction } },
      ...(index === 1 ? { assertions: [{ path: "objective.nextRelay", operator: "equals", expected: "beta" }] } : {}),
      ...(index === 5 ? { assertions: [{ path: "objective.nextRelay", operator: "equals", expected: "gamma" }] } : {}),
      ...(index === 9 ? { assertions: [{ path: "objective.exitUnlocked", operator: "equals", expected: true }] } : {})
    }))
  ],
  finalAssertions: [
    { path: "lifecycle.status", operator: "equals", expected: "won" },
    { path: "objective.relaysActivated", operator: "equals", expected: 3 },
    { path: "stats.moves", operator: "equals", expected: 16 },
    { path: "player.score", operator: "greaterThanOrEqual", expected: 500 }
  ]
};

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

  const pauseScenario = {
    name: "pause gates movement and resume restores it",
    seed: 42,
    steps: [
      { action: { kind: "bridge", name: "start" } },
      { action: { kind: "bridge", name: "togglePause" }, assertions: [{ path: "lifecycle.paused", operator: "equals", expected: true }] },
      { action: { kind: "bridge", name: "move", payload: { direction: "right" } }, assertions: [{ path: "player.position.x", operator: "equals", expected: 0 }] },
      { action: { kind: "bridge", name: "togglePause" } },
      { action: { kind: "bridge", name: "move", payload: { direction: "right" } } }
    ],
    finalAssertions: [
      { path: "lifecycle.paused", operator: "equals", expected: false },
      { path: "player.position.x", operator: "equals", expected: 1 }
    ]
  };
  const pauseRun = await call("web2d_scenario_run", { sessionId, scenario: pauseScenario });
  const quality = await call("web2d_quality_check", { sessionId });
  const deterministicReplay = JSON.stringify(winningRun1.finalState) === JSON.stringify(winningRun2.finalState);
  const passed = initial.state.lifecycle.seed === 42
    && nativeInput.passed
    && winningRun1.passed
    && winningRun2.passed
    && deterministicReplay
    && pauseRun.passed
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
    qualityCheck: quality.passed
  }, null, 2));
} finally {
  if (sessionId) {
    await client.callTool({ name: "web2d_session_stop", arguments: { sessionId } }).catch(() => undefined);
  }
  await client.close();
  await gameServer?.close();
}
