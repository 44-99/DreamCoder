export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
export type GameState = Record<string, JsonValue>;

export type GameAction =
  | { kind: "key"; key: string; phase?: "press" | "down" | "up"; durationMs?: number }
  | { kind: "pointer"; x: number; y: number; phase?: "click" | "down" | "up"; button?: "left" | "middle" | "right" }
  | { kind: "wait"; durationMs?: number; frames?: number }
  | { kind: "bridge"; name: string; payload?: JsonValue };

export type AssertionOperator =
  | "equals"
  | "notEquals"
  | "greaterThan"
  | "greaterThanOrEqual"
  | "lessThan"
  | "lessThanOrEqual"
  | "includes"
  | "exists";

export interface GameAssertion {
  path: string;
  operator: AssertionOperator;
  expected?: JsonValue;
  message?: string;
}

export interface AssertionResult {
  assertion: GameAssertion;
  actual?: JsonValue;
  passed: boolean;
  message: string;
}

export interface ScenarioStep {
  action: GameAction;
  assertions?: GameAssertion[];
}

export interface GameScenario {
  name: string;
  seed?: number;
  steps: ScenarioStep[];
  finalAssertions?: GameAssertion[];
}

export interface BridgeDescriptor {
  protocolVersion: "1";
  name: string;
  framework?: string;
  capabilities?: string[];
}

export interface Web2DGameBridge {
  describe(): BridgeDescriptor | Promise<BridgeDescriptor>;
  getState(): GameState | Promise<GameState>;
  reset(options?: { seed?: number }): void | Promise<void>;
  dispatch?(action: { name: string; payload?: JsonValue }): void | Promise<void>;
  step?(frames: number): void | Promise<void>;
  getMetrics?(): Record<string, JsonValue> | Promise<Record<string, JsonValue>>;
}

export interface ToolError {
  code: string;
  message: string;
  hint?: string;
  details?: JsonValue;
}

export type ToolEnvelope<T> = { ok: true; data: T } | { ok: false; error: ToolError };

declare global {
  interface Window {
    __WEB2D_GAME__?: Web2DGameBridge;
  }
}
