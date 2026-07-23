import { createServer, type Server } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { SessionManager } from "../src/core/session-manager.js";

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
});
