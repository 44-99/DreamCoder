const canvas = document.querySelector("#game");
const context = canvas.getContext("2d");
let state;

function reset(seed = 1) {
  state = { scene: "grid", status: "playing", seed, player: { x: 1, y: 1 }, moves: 0, ticks: 0 };
  render();
}

function move(dx, dy) {
  state.player.x = Math.max(0, Math.min(7, state.player.x + dx));
  state.player.y = Math.max(0, Math.min(5, state.player.y + dy));
  state.moves += 1;
  render();
}

function render() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = "#334a67";
  for (let x = 0; x <= 320; x += 40) { context.beginPath(); context.moveTo(x, 0); context.lineTo(x, 240); context.stroke(); }
  for (let y = 0; y <= 240; y += 40) { context.beginPath(); context.moveTo(0, y); context.lineTo(320, y); context.stroke(); }
  context.fillStyle = "#50d5ff";
  context.fillRect(state.player.x * 40 + 8, state.player.y * 40 + 8, 24, 24);
}

window.addEventListener("keydown", (event) => {
  const directions = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
  const direction = directions[event.key];
  if (direction) move(...direction);
});

window.__WEB2D_GAME__ = {
  describe: () => ({ protocolVersion: "1", name: "bridge-demo", framework: "Canvas 2D", capabilities: ["state", "reset", "dispatch", "step"] }),
  getState: () => structuredClone(state),
  reset: ({ seed } = {}) => reset(seed ?? 1),
  dispatch: ({ name, payload }) => {
    if (name !== "move") throw new Error(`Unknown action: ${name}`);
    move(payload.dx, payload.dy);
  },
  step: (frames) => { state.ticks += frames; },
  getMetrics: () => ({ logicalTicks: state.ticks })
};

reset();
