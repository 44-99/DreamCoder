import { SessionManager } from "../core/session-manager.js";
import type { LoadedScenario } from "./schema.js";

type ScenarioRunResult = Awaited<ReturnType<SessionManager["runScenario"]>>;

export interface ScenarioSuiteEntry {
  file: string;
  name: string;
  passed: boolean;
  result?: ScenarioRunResult;
  error?: string;
}

export interface ScenarioSuiteResult {
  passed: boolean;
  total: number;
  passedCount: number;
  failedCount: number;
  scenarios: ScenarioSuiteEntry[];
}

export interface RunScenarioSuiteOptions {
  url: string;
  scenarios: LoadedScenario[];
  width?: number;
  height?: number;
  headless?: boolean;
}

export async function runScenarioSuite(options: RunScenarioSuiteOptions): Promise<ScenarioSuiteResult> {
  const sessions = new SessionManager();
  let sessionId: string | undefined;
  const entries: ScenarioSuiteEntry[] = [];
  try {
    const started = await sessions.start({
      url: options.url,
      seed: options.scenarios[0]?.scenario.seed ?? 1,
      width: options.width,
      height: options.height,
      headless: options.headless
    });
    sessionId = started.sessionId;
    if (!started.bridge) throw new Error("Game Bridge not found. Scenario suites require structured game state.");

    for (const loaded of options.scenarios) {
      try {
        const result = await sessions.runScenario(sessionId, loaded.scenario);
        entries.push({ file: loaded.file, name: loaded.scenario.name, passed: result.passed, result });
      } catch (error) {
        entries.push({
          file: loaded.file,
          name: loaded.scenario.name,
          passed: false,
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }
  } finally {
    if (sessionId) await sessions.stop(sessionId).catch(() => undefined);
    await sessions.closeAll();
  }

  const passedCount = entries.filter((entry) => entry.passed).length;
  return {
    passed: passedCount === entries.length,
    total: entries.length,
    passedCount,
    failedCount: entries.length - passedCount,
    scenarios: entries
  };
}

export function formatScenarioSuite(result: ScenarioSuiteResult, reporter: "text" | "json"): string {
  if (reporter === "json") return JSON.stringify(result, null, 2);
  const lines: string[] = [];
  for (const entry of result.scenarios) {
    lines.push(`${entry.passed ? "PASS" : "FAIL"} ${entry.file} — ${entry.name}`);
    if (entry.error) lines.push(`  ${entry.error}`);
    for (const failure of entry.result?.failures ?? []) {
      lines.push(`  ${String(failure.step)}`);
      for (const assertion of failure.results.filter((item) => !item.passed)) lines.push(`    ${assertion.message}`);
    }
  }
  lines.push(`${result.total} scenarios: ${result.passedCount} passed, ${result.failedCount} failed`);
  return lines.join("\n");
}
