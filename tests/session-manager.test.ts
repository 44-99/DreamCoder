import { createServer, type Server } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { SessionManager } from "../src/core/session-manager.js";
import { runScenarioSuite } from "../src/scenarios/runner.js";

let server: Server;
let baseUrl: string;
const sessions = new SessionManager();

beforeAll(async () => {
  const html = await readFile(path.resolve("examples/bridge-demo/index.html"));
  const script = await readFile(path.resolve("examples/bridge-demo/game.js"));
  server = createServer((request, response) => {
    if (request.url === "/plain") {
      response.writeHead(200, { "content-type": "text/html" });
      response.end("<!doctype html><title>Plain game page</title><button>Play</button>");
      return;
    }
    if (request.url === "/game.js") {
      response.writeHead(200, { "content-type": "text/javascript" });
      response.end(script);
      return;
    }
    response.writeHead(200, { "content-type": "text/html" });
    response.end(html);
  });
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("Test server did not bind a TCP port.");
  baseUrl = `http://127.0.0.1:${address.port}`;
});

afterAll(async () => {
  await sessions.closeAll();
  await new Promise<void>((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
});

describe("controlled gameplay session", () => {
  it("starts a page without requiring the optional game bridge", async () => {
    const started = await sessions.start({ url: `${baseUrl}/plain`, seed: 42 });

    expect(started).toMatchObject({ seed: 42, bridge: null, title: "Plain game page" });
    await sessions.stop(started.sessionId);
  });

  it("observes, acts, replays, and checks a bridge-enabled game", async () => {
    const started = await sessions.start({ url: baseUrl, seed: 42 });
    expect(started.bridge?.protocolVersion).toBe("1");

    const initial = await sessions.observe(started.sessionId);
    expect(initial.state).toMatchObject({ seed: 42, player: { x: 1, y: 1 }, moves: 0 });

    const progress: number[] = [];
    const result = await sessions.runScenario(started.sessionId, {
      name: "move-right",
      seed: 42,
      steps: [
        {
          action: { kind: "bridge", name: "move", payload: { dx: 1, dy: 0 } },
          assertions: [{ path: "player.x", operator: "equals", expected: 2 }]
        }
      ],
      finalAssertions: [{ path: "moves", operator: "equals", expected: 1 }]
    }, { onProgress: (completed) => progress.push(completed) });

    expect(result.passed).toBe(true);
    expect(progress).toEqual([1]);
    expect((await sessions.qualityCheck(started.sessionId)).passed).toBe(true);
    await sessions.stop(started.sessionId);
  });

  it("stops before actions when initial assertions fail", async () => {
    const started = await sessions.start({ url: baseUrl, seed: 42 });
    const result = await sessions.runScenario(started.sessionId, {
      name: "reject-wrong-starting-state",
      seed: 42,
      initialAssertions: [{ path: "player.x", operator: "equals", expected: 99 }],
      steps: [
        { action: { kind: "bridge", name: "move", payload: { dx: 1, dy: 0 } } }
      ]
    });

    expect(result.passed).toBe(false);
    expect(result.completedSteps).toBe(0);
    expect(result.failures).toHaveLength(1);
    expect(result.failures[0]?.step).toBe("initial");
    expect(result.finalState).toMatchObject({ player: { x: 1, y: 1 }, moves: 0 });
    await sessions.stop(started.sessionId);
  });

  it("runs the complete suite after an earlier scenario fails", async () => {
    const result = await runScenarioSuite({
      url: baseUrl,
      scenarios: [
        {
          file: "01-fails.web2d.json",
          scenario: {
            schemaVersion: "1",
            name: "fails first",
            initialAssertions: [{ path: "moves", operator: "equals", expected: 99 }],
            steps: []
          }
        },
        {
          file: "02-passes.web2d.json",
          scenario: {
            schemaVersion: "1",
            name: "still runs",
            initialAssertions: [{ path: "moves", operator: "equals", expected: 0 }],
            steps: []
          }
        }
      ]
    });

    expect(result).toMatchObject({ passed: false, total: 2, passedCount: 1, failedCount: 1 });
    expect(result.scenarios.map((entry) => entry.name)).toEqual(["fails first", "still runs"]);
  });
});
