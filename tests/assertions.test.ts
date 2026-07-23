import { describe, expect, it } from "vitest";
import { evaluateAssertions, readStatePath } from "../src/core/assertions.js";

describe("structured game assertions", () => {
  const state = {
    scene: "level-1",
    player: { health: 80, position: { x: 4, y: 2 }, inventory: ["key", "map"] },
    paused: false
  };

  it("reads dotted and indexed paths without evaluating code", () => {
    expect(readStatePath(state, "player.position.x")).toBe(4);
    expect(readStatePath(state, "player.inventory[1]")).toBe("map");
    expect(readStatePath(state, "constructor.prototype")).toBeUndefined();
  });

  it("reports actionable pass and failure results", () => {
    const results = evaluateAssertions(state, [
      { path: "scene", operator: "equals", expected: "level-1" },
      { path: "player.health", operator: "greaterThan", expected: 0 },
      { path: "player.inventory", operator: "includes", expected: "key" },
      { path: "paused", operator: "equals", expected: true }
    ]);

    expect(results.map((result) => result.passed)).toEqual([true, true, true, false]);
    expect(results[3]?.message).toContain("received false");
  });
});
