import { describe, expect, it } from "vitest";
import { applyAction, createInitialState, type Direction, type GameState } from "../src/domain";

function start(seed = 42): GameState {
  return applyAction(createInitialState(seed), { name: "start" });
}

function move(state: GameState, ...directions: Direction[]): GameState {
  return directions.reduce((current, direction) => applyAction(current, { name: "move", payload: { direction } }), state);
}

describe("Signal Relay rules", () => {
  it("activates relays in sequence and completes the mission", () => {
    let state = start();
    state = move(state, "right", "down");
    expect(state.objective.nextRelay).toBe("beta");
    state = move(state, "right", "right", "right", "right");
    expect(state.objective.nextRelay).toBe("gamma");
    state = move(state, "down", "down", "down", "down");
    expect(state.objective.exitUnlocked).toBe(true);
    state = move(state, "down", "left", "left", "left", "left", "left");
    expect(state.lifecycle.status).toBe("won");
    expect(state.player.score).toBeGreaterThanOrEqual(500);
  });

  it("does not spend energy on a blocked move", () => {
    const state = move(start(), "left");
    expect(state.player.energy).toBe(18);
    expect(state.stats.moves).toBe(0);
  });

  it("ignores movement while paused and resets deterministically", () => {
    let state = applyAction(start(7), { name: "togglePause" });
    state = move(state, "right");
    expect(state.player.position).toEqual({ x: 0, y: 0 });
    const reset = applyAction(state, { name: "restart", payload: { seed: 7 } });
    expect(reset).toEqual(createInitialState(7));
  });
});
