import type { BridgeDescriptor, GameState, JsonValue, Web2DGameBridge } from "../types.js";

export interface BridgeAdapter {
  name: string;
  framework?: string;
  capabilities?: string[];
  getState(): GameState | Promise<GameState>;
  reset(options?: { seed?: number }): void | Promise<void>;
  dispatch?(action: { name: string; payload?: JsonValue }): void | Promise<void>;
  step?(frames: number): void | Promise<void>;
  getMetrics?(): Record<string, JsonValue> | Promise<Record<string, JsonValue>>;
}

export function createWeb2DBridge(adapter: BridgeAdapter): Web2DGameBridge {
  if (!adapter.name.trim()) throw new Error("A bridge name is required.");

  const descriptor: BridgeDescriptor = {
    protocolVersion: "1",
    name: adapter.name,
    ...(adapter.framework ? { framework: adapter.framework } : {}),
    capabilities: adapter.capabilities ?? ["state", "reset"]
  };

  return {
    describe: () => descriptor,
    getState: () => adapter.getState(),
    reset: (options) => adapter.reset(options),
    ...(adapter.dispatch ? { dispatch: (action) => adapter.dispatch!(action) } : {}),
    ...(adapter.step ? { step: (frames) => adapter.step!(frames) } : {}),
    ...(adapter.getMetrics ? { getMetrics: () => adapter.getMetrics!() } : {})
  };
}

export function installWeb2DBridge(adapter: BridgeAdapter, target: Window = window): Web2DGameBridge {
  const bridge = createWeb2DBridge(adapter);
  target.__WEB2D_GAME__ = bridge;
  return bridge;
}
