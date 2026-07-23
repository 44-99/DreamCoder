import { randomUUID } from "node:crypto";
import { chromium, type Browser, type BrowserContext, type Page } from "playwright";
import { evaluateAssertions } from "./assertions.js";
import type {
  AssertionResult,
  BridgeDescriptor,
  GameAction,
  GameAssertion,
  GameScenario,
  GameState,
  JsonValue
} from "../types.js";

interface SessionDiagnostics {
  consoleErrors: string[];
  pageErrors: string[];
  requestFailures: string[];
}

interface ManagedSession {
  id: string;
  browser: Browser;
  context: BrowserContext;
  page: Page;
  url: string;
  seed: number;
  diagnostics: SessionDiagnostics;
}

export interface StartSessionOptions {
  url: string;
  seed?: number;
  width?: number;
  height?: number;
  headless?: boolean;
}

export interface SessionSummary {
  sessionId: string;
  url: string;
  seed: number;
  bridge: BridgeDescriptor | null;
  title: string;
}

export interface ScenarioRunOptions {
  signal?: AbortSignal;
  onProgress?: (completed: number, total: number) => void | Promise<void>;
}

function requireWebUrl(value: string): URL {
  const url = new URL(value);
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("Only http:// and https:// game URLs are allowed.");
  }
  return url;
}

function capPush(values: string[], value: string): void {
  if (values.length < 100) values.push(value);
}

export class SessionManager {
  private readonly sessions = new Map<string, ManagedSession>();

  async start(options: StartSessionOptions): Promise<SessionSummary> {
    const url = requireWebUrl(options.url).toString();
    const seed = options.seed ?? 1;
    const browser = await chromium.launch({ headless: options.headless ?? true });
    const context = await browser.newContext({
      viewport: { width: options.width ?? 1280, height: options.height ?? 720 },
      reducedMotion: "reduce"
    });

    await context.addInitScript((initialSeed: number) => {
      let state = initialSeed >>> 0;
      Math.random = () => {
        state += 0x6d2b79f5;
        let value = state;
        value = Math.imul(value ^ (value >>> 15), value | 1);
        value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
        return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
      };
    }, seed);

    const page = await context.newPage();
    const diagnostics: SessionDiagnostics = { consoleErrors: [], pageErrors: [], requestFailures: [] };
    page.on("console", (message) => {
      if (message.type() === "error") capPush(diagnostics.consoleErrors, message.text());
    });
    page.on("pageerror", (error) => capPush(diagnostics.pageErrors, error.message));
    page.on("requestfailed", (request) => {
      capPush(diagnostics.requestFailures, `${request.method()} ${request.url()}: ${request.failure()?.errorText ?? "failed"}`);
    });

    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
      const id = randomUUID();
      const session: ManagedSession = { id, browser, context, page, url, seed, diagnostics };
      const bridge = await this.describeBridge(session);
      if (bridge) {
        await page.evaluate(async (initialSeed) => {
          await window.__WEB2D_GAME__?.reset({ seed: initialSeed });
        }, seed);
      }
      const title = await page.title();
      this.sessions.set(id, session);
      return {
        sessionId: id,
        url,
        seed,
        bridge,
        title
      };
    } catch (error) {
      await browser.close();
      throw error;
    }
  }

  async stop(sessionId: string): Promise<{ sessionId: string; stopped: true }> {
    const session = this.requireSession(sessionId);
    this.sessions.delete(sessionId);
    await session.browser.close();
    return { sessionId, stopped: true };
  }

  async observe(sessionId: string): Promise<{
    sessionId: string;
    bridge: BridgeDescriptor;
    state: GameState;
    metrics?: Record<string, JsonValue>;
  }> {
    const session = this.requireSession(sessionId);
    const result = await session.page.evaluate(async () => {
      const bridge = window.__WEB2D_GAME__;
      if (!bridge) return null;
      return {
        bridge: await bridge.describe(),
        state: await bridge.getState(),
        metrics: bridge.getMetrics ? await bridge.getMetrics() : undefined
      };
    });

    if (!result) {
      throw new Error("Game Bridge not found. Install window.__WEB2D_GAME__ before requesting structured state.");
    }
    if (!result.state || typeof result.state !== "object" || Array.isArray(result.state)) {
      throw new Error("Game Bridge getState() must return a JSON object.");
    }
    return { sessionId, ...result };
  }

  async act(sessionId: string, actions: GameAction[]): Promise<{ sessionId: string; actionsCompleted: number; state?: GameState }> {
    const session = this.requireSession(sessionId);
    for (const action of actions) await this.performAction(session, action);

    const hasBridge = await this.hasBridge(session);
    return {
      sessionId,
      actionsCompleted: actions.length,
      ...(hasBridge ? { state: (await this.observe(sessionId)).state } : {})
    };
  }

  async assert(sessionId: string, assertions: GameAssertion[]): Promise<{
    sessionId: string;
    passed: boolean;
    results: AssertionResult[];
  }> {
    const state = (await this.observe(sessionId)).state;
    const results = evaluateAssertions(state, assertions);
    return { sessionId, passed: results.every((result) => result.passed), results };
  }

  async runScenario(sessionId: string, scenario: GameScenario, options: ScenarioRunOptions = {}): Promise<{
    sessionId: string;
    scenario: string;
    passed: boolean;
    completedSteps: number;
    failures: Array<{ step: number | "final"; results: AssertionResult[] }>;
    finalState: GameState;
  }> {
    const session = this.requireSession(sessionId);
    await session.page.evaluate(async (seed) => {
      const bridge = window.__WEB2D_GAME__;
      if (!bridge) throw new Error("Game Bridge not found.");
      await bridge.reset({ seed });
    }, scenario.seed ?? session.seed);

    const failures: Array<{ step: number | "final"; results: AssertionResult[] }> = [];
    let completedSteps = 0;
    for (const [index, step] of scenario.steps.entries()) {
      if (options.signal?.aborted) throw new Error("Scenario was cancelled by the MCP client.");
      await this.performAction(session, step.action);
      completedSteps += 1;
      if (step.assertions?.length) {
        const state = (await this.observe(sessionId)).state;
        const results = evaluateAssertions(state, step.assertions);
        if (results.some((result) => !result.passed)) failures.push({ step: index + 1, results });
      }
      await options.onProgress?.(completedSteps, scenario.steps.length);
    }

    const finalState = (await this.observe(sessionId)).state;
    if (scenario.finalAssertions?.length) {
      const results = evaluateAssertions(finalState, scenario.finalAssertions);
      if (results.some((result) => !result.passed)) failures.push({ step: "final", results });
    }

    return {
      sessionId,
      scenario: scenario.name,
      passed: failures.length === 0,
      completedSteps,
      failures,
      finalState
    };
  }

  async qualityCheck(sessionId: string): Promise<{
    sessionId: string;
    passed: boolean;
    checks: Array<{ name: string; passed: boolean; detail: string }>;
    diagnostics: SessionDiagnostics;
  }> {
    const session = this.requireSession(sessionId);
    const pageFacts = await session.page.evaluate(async () => {
      const bridge = window.__WEB2D_GAME__;
      let stateReadable = false;
      if (bridge) {
        try {
          const state = await bridge.getState();
          JSON.stringify(state);
          stateReadable = Boolean(state && typeof state === "object" && !Array.isArray(state));
        } catch {
          stateReadable = false;
        }
      }
      return {
        bridgeAvailable: Boolean(bridge),
        stateReadable,
        canvasCount: document.querySelectorAll("canvas").length,
        svgCount: document.querySelectorAll("svg").length,
        interactiveCount: document.querySelectorAll("button, a, input, [tabindex]").length
      };
    });

    const checks = [
      { name: "bridge-available", passed: pageFacts.bridgeAvailable, detail: "window.__WEB2D_GAME__ is available" },
      { name: "state-readable", passed: pageFacts.stateReadable, detail: "getState() returns serializable structured state" },
      {
        name: "runtime-errors",
        passed: session.diagnostics.consoleErrors.length === 0 && session.diagnostics.pageErrors.length === 0,
        detail: `${session.diagnostics.consoleErrors.length + session.diagnostics.pageErrors.length} runtime error(s)`
      },
      {
        name: "resource-loads",
        passed: session.diagnostics.requestFailures.length === 0,
        detail: `${session.diagnostics.requestFailures.length} failed request(s)`
      },
      {
        name: "render-surface",
        passed: pageFacts.canvasCount + pageFacts.svgCount + pageFacts.interactiveCount > 0,
        detail: `${pageFacts.canvasCount} canvas, ${pageFacts.svgCount} SVG, ${pageFacts.interactiveCount} interactive DOM element(s)`
      }
    ];

    return { sessionId, passed: checks.every((check) => check.passed), checks, diagnostics: session.diagnostics };
  }

  async closeAll(): Promise<void> {
    const sessions = [...this.sessions.values()];
    this.sessions.clear();
    await Promise.allSettled(sessions.map((session) => session.browser.close()));
  }

  private requireSession(sessionId: string): ManagedSession {
    const session = this.sessions.get(sessionId);
    if (!session) throw new Error(`Unknown session: ${sessionId}`);
    return session;
  }

  private async hasBridge(session: ManagedSession): Promise<boolean> {
    return session.page.evaluate(() => Boolean(window.__WEB2D_GAME__));
  }

  private async describeBridge(session: ManagedSession): Promise<BridgeDescriptor | null> {
    return session.page.evaluate(async () => window.__WEB2D_GAME__ ? window.__WEB2D_GAME__.describe() : null);
  }

  private async performAction(session: ManagedSession, action: GameAction): Promise<void> {
    switch (action.kind) {
      case "key": {
        const phase = action.phase ?? "press";
        if (phase === "down") await session.page.keyboard.down(action.key);
        else if (phase === "up") await session.page.keyboard.up(action.key);
        else await session.page.keyboard.press(action.key, { delay: action.durationMs ?? 0 });
        break;
      }
      case "pointer": {
        const phase = action.phase ?? "click";
        await session.page.mouse.move(action.x, action.y);
        if (phase === "down") await session.page.mouse.down({ button: action.button ?? "left" });
        else if (phase === "up") await session.page.mouse.up({ button: action.button ?? "left" });
        else await session.page.mouse.click(action.x, action.y, { button: action.button ?? "left" });
        break;
      }
      case "wait": {
        if (action.frames !== undefined) {
          const stepped = await session.page.evaluate(async (frames) => {
            const bridge = window.__WEB2D_GAME__;
            if (!bridge?.step) return false;
            await bridge.step(frames);
            return true;
          }, action.frames);
          if (!stepped) await session.page.waitForTimeout(Math.ceil(action.frames * (1000 / 60)));
        } else {
          await session.page.waitForTimeout(action.durationMs ?? 0);
        }
        break;
      }
      case "bridge": {
        const serializedAction = JSON.stringify(action);
        await session.page.evaluate(async (serialized) => {
          const { name, payload } = JSON.parse(serialized) as { name: string; payload?: JsonValue };
          const bridge = window.__WEB2D_GAME__;
          if (!bridge?.dispatch) throw new Error("Game Bridge does not implement dispatch().");
          await bridge.dispatch({ name, ...(payload === undefined ? {} : { payload }) });
        }, serializedAction);
        break;
      }
    }
  }
}
