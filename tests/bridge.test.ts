import { describe, expect, it, vi } from "vitest";
import { createWeb2DBridge } from "../src/bridge/index.js";

describe("Game Bridge", () => {
  it("wraps a framework-neutral adapter with protocol metadata", async () => {
    const reset = vi.fn();
    const bridge = createWeb2DBridge({
      name: "puzzle-demo",
      framework: "Canvas 2D",
      getState: () => ({ moves: 2, status: "playing" }),
      reset
    });

    expect(await bridge.describe()).toMatchObject({
      protocolVersion: "1",
      name: "puzzle-demo",
      framework: "Canvas 2D"
    });
    expect(await bridge.getState()).toEqual({ moves: 2, status: "playing" });
    await bridge.reset({ seed: 7 });
    expect(reset).toHaveBeenCalledWith({ seed: 7 });
  });
});
