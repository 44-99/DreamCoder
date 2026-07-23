#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { ProjectBoundary, inspectProject } from "./core/project-inspector.js";
import { SessionManager } from "./core/session-manager.js";
import { ActionSchema, AssertionSchema, GameScenarioSchema } from "./scenarios/schema.js";
import type { GameAction, GameAssertion, GameScenario, ToolEnvelope } from "./types.js";

const ErrorSchema = z.object({
  code: z.string(),
  message: z.string(),
  hint: z.string().optional(),
  details: z.unknown().optional()
});

const EnvelopeSchema = z.object({
  ok: z.boolean(),
  data: z.unknown().optional(),
  error: ErrorSchema.optional()
});

function errorCode(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  if (message.includes("Unknown session")) return "SESSION_NOT_FOUND";
  if (message.includes("Game Bridge")) return "BRIDGE_NOT_AVAILABLE";
  if (message.includes("WEB2DKIT_ROOT") || message.includes("escapes")) return "PROJECT_BOUNDARY_VIOLATION";
  if (message.includes("browserType.launch")) return "BROWSER_NOT_INSTALLED";
  if (message.includes("cancelled by the MCP client")) return "SCENARIO_CANCELLED";
  return "TOOL_EXECUTION_FAILED";
}

function hintFor(code: string): string | undefined {
  if (code === "BROWSER_NOT_INSTALLED") return "Run `npx playwright install chromium` once, then retry.";
  if (code === "BRIDGE_NOT_AVAILABLE") return "Install the Web2DKit Game Bridge in the game page and reload the session.";
  if (code === "PROJECT_BOUNDARY_VIOLATION") return "Use a relative path inside WEB2DKIT_ROOT.";
  return undefined;
}

function success<T>(data: T): ToolEnvelope<T> {
  return { ok: true, data };
}

function failure(error: unknown): ToolEnvelope<never> {
  const code = errorCode(error);
  return {
    ok: false,
    error: {
      code,
      message: error instanceof Error ? error.message : String(error),
      ...(hintFor(code) ? { hint: hintFor(code) } : {})
    }
  };
}

function toolResult(envelope: ToolEnvelope<unknown>): CallToolResult {
  return {
    content: [{ type: "text", text: JSON.stringify(envelope, null, 2) }],
    structuredContent: envelope as unknown as Record<string, unknown>,
    ...(!envelope.ok ? { isError: true } : {})
  };
}

async function runTool<T>(operation: () => Promise<T>): Promise<CallToolResult> {
  try {
    return toolResult(success(await operation()));
  } catch (error) {
    return toolResult(failure(error));
  }
}

const sessions = new SessionManager();
const server = new McpServer(
  { name: "web2dkit", version: "0.1.0" },
  { capabilities: { logging: {} } }
);

let boundaryPromise: Promise<ProjectBoundary> | undefined;
function getProjectBoundary(): Promise<ProjectBoundary> {
  if (!boundaryPromise) {
    boundaryPromise = (async () => {
      if (process.env.WEB2DKIT_ROOT) return ProjectBoundary.create(process.env.WEB2DKIT_ROOT);
      if (server.server.getClientCapabilities()?.roots) {
        const listed = await server.server.listRoots();
        const fileRoot = listed.roots.find((root) => root.uri.startsWith("file:"));
        if (fileRoot) return ProjectBoundary.create(fileURLToPath(fileRoot.uri));
      }
      return ProjectBoundary.create(process.cwd());
    })();
  }
  return boundaryPromise;
}

server.registerTool(
  "web2d_project_inspect",
  {
    title: "Inspect a Web 2D game project",
    description: "Detect the browser-game stack, entry points, scripts, and Web2DKit Game Bridge coverage inside the configured project root.",
    inputSchema: z.object({ path: z.string().default(".").describe("Relative path inside WEB2DKIT_ROOT") }),
    outputSchema: EnvelopeSchema,
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
  },
  ({ path }) => runTool(async () => inspectProject(await (await getProjectBoundary()).resolve(path)))
);

server.registerTool(
  "web2d_session_start",
  {
    title: "Start a controlled game session",
    description: "Open a browser-native 2D game with a fixed random seed and collect runtime diagnostics. The game server must already be running.",
    inputSchema: z.object({
      url: z.string().url(),
      seed: z.number().int().min(0).max(0xffffffff).default(1),
      width: z.number().int().min(320).max(3840).default(1280),
      height: z.number().int().min(240).max(2160).default(720),
      headless: z.boolean().default(true)
    }),
    outputSchema: EnvelopeSchema,
    annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true }
  },
  (options) => runTool(() => sessions.start(options))
);

server.registerTool(
  "web2d_session_stop",
  {
    title: "Stop a controlled game session",
    description: "Close a Web2DKit browser session and release its resources.",
    inputSchema: z.object({ sessionId: z.string().uuid() }),
    outputSchema: EnvelopeSchema,
    annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false }
  },
  ({ sessionId }) => runTool(() => sessions.stop(sessionId))
);

server.registerTool(
  "web2d_observe",
  {
    title: "Observe structured game state",
    description: "Read the current scene, entities, rules, score, and metrics through the Web2DKit Game Bridge instead of inferring them from pixels.",
    inputSchema: z.object({ sessionId: z.string().uuid() }),
    outputSchema: EnvelopeSchema,
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
  },
  ({ sessionId }) => runTool(() => sessions.observe(sessionId))
);

server.registerTool(
  "web2d_act",
  {
    title: "Perform game actions",
    description: "Send bounded keyboard, pointer, timing, or domain bridge actions to a controlled game session.",
    inputSchema: z.object({ sessionId: z.string().uuid(), actions: z.array(ActionSchema).min(1).max(100) }),
    outputSchema: EnvelopeSchema,
    annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false }
  },
  ({ sessionId, actions }) => runTool(() => sessions.act(sessionId, actions as GameAction[]))
);

server.registerTool(
  "web2d_assert",
  {
    title: "Assert game rules",
    description: "Evaluate explicit assertions against structured game state and return self-correctable failures.",
    inputSchema: z.object({ sessionId: z.string().uuid(), assertions: z.array(AssertionSchema).min(1).max(100) }),
    outputSchema: EnvelopeSchema,
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
  },
  ({ sessionId, assertions }) => runTool(() => sessions.assert(sessionId, assertions as GameAssertion[]))
);

server.registerTool(
  "web2d_scenario_run",
  {
    title: "Run a deterministic gameplay scenario",
    description: "Reset with a seed, replay bounded actions, evaluate step and final assertions, and return the exact failing step.",
    inputSchema: z.object({ sessionId: z.string().uuid(), scenario: GameScenarioSchema }),
    outputSchema: EnvelopeSchema,
    annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false }
  },
  ({ sessionId, scenario }, extra) => runTool(() => {
    const progressToken = extra._meta?.progressToken;
    return sessions.runScenario(sessionId, scenario as unknown as GameScenario, {
      signal: extra.signal,
      onProgress: progressToken === undefined ? undefined : (completed, total) => extra.sendNotification({
        method: "notifications/progress",
        params: { progressToken, progress: completed, total }
      })
    });
  })
);

server.registerTool(
  "web2d_quality_check",
  {
    title: "Check Web 2D runtime quality",
    description: "Check bridge readiness, serializable state, runtime errors, failed resources, and the presence of a render or interaction surface.",
    inputSchema: z.object({ sessionId: z.string().uuid() }),
    outputSchema: EnvelopeSchema,
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
  },
  ({ sessionId }) => runTool(() => sessions.qualityCheck(sessionId))
);

const shutdown = async (): Promise<void> => {
  await sessions.closeAll();
  await server.close();
};
process.once("SIGINT", () => void shutdown().finally(() => process.exit(0)));
process.once("SIGTERM", () => void shutdown().finally(() => process.exit(0)));

await server.connect(new StdioServerTransport());
