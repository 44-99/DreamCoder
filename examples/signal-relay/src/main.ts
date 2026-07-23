import "./styles.css";
import { applyAction, BOARD_SIZE, createInitialState, MAX_ENERGY, type Direction, type DomainAction, type GameState } from "./domain";

const board = document.querySelector<HTMLDivElement>("#game-board")!;
const overlay = document.querySelector<HTMLDivElement>("#game-overlay")!;
const pauseButton = document.querySelector<HTMLButtonElement>("#pause-button")!;
const energyValue = document.querySelector<HTMLElement>("#energy-value")!;
const energyBar = document.querySelector<HTMLElement>("#energy-bar")!;
const scoreValue = document.querySelector<HTMLElement>("#score-value")!;
const movesValue = document.querySelector<HTMLElement>("#moves-value")!;
const progress = document.querySelector<HTMLElement>("#relay-progress")!;
const directive = document.querySelector<HTMLElement>("#directive")!;
const statusMessage = document.querySelector<HTMLElement>("#status-message")!;
const seedValue = document.querySelector<HTMLElement>("#seed-value")!;

let state = createInitialState(1);

function dispatch(action: DomainAction): void {
  state = applyAction(state, action);
  render();
}

function entityMarkup(x: number, y: number): string {
  const relay = state.relays.find((candidate) => candidate.x === x && candidate.y === y);
  const hazard = state.hazards.find((candidate) => candidate.x === x && candidate.y === y);
  const isCharge = !state.charge.collected && state.charge.x === x && state.charge.y === y;
  const isExit = state.exit.x === x && state.exit.y === y;
  const isPlayer = state.player.position.x === x && state.player.position.y === y;

  return [
    isExit ? `<span class="exit ${state.objective.exitUnlocked ? "unlocked" : ""}" aria-label="Uplink exit">⌁</span>` : "",
    hazard ? `<span class="hazard" aria-label="Interference hazard">×</span>` : "",
    isCharge ? `<span class="charge" aria-label="Energy charge">+</span>` : "",
    relay ? `<span class="relay ${relay.active ? "active" : ""}" aria-label="Relay ${relay.label}${relay.active ? " active" : ""}">${relay.label}</span>` : "",
    isPlayer ? `<span class="player" aria-label="Courier"></span>` : ""
  ].join("");
}

function overlayMarkup(): string {
  if (state.lifecycle.status === "ready") {
    return `<div class="overlay-card"><span class="overlay-code">LINK READY</span><h2>Enter Sector 07</h2><p>Restore three relays in sequence. Every move costs one energy.</p><button id="primary-action" type="button">Begin mission</button></div>`;
  }
  if (state.lifecycle.paused) {
    return `<div class="overlay-card compact"><span class="overlay-code">SUSPENDED</span><h2>Mission paused</h2><button id="primary-action" type="button">Resume</button></div>`;
  }
  if (state.lifecycle.status === "won") {
    return `<div class="overlay-card"><span class="overlay-code success">TRANSMISSION COMPLETE</span><h2>Sector restored</h2><p>Final score ${state.player.score.toString().padStart(4, "0")} · ${state.player.energy} energy remaining</p><button id="primary-action" type="button">Run again</button></div>`;
  }
  if (state.lifecycle.status === "lost") {
    return `<div class="overlay-card"><span class="overlay-code danger">SIGNAL LOST</span><h2>Courier depleted</h2><p>The route consumed all available energy.</p><button id="primary-action" type="button">Retry mission</button></div>`;
  }
  return "";
}

function render(): void {
  board.replaceChildren();
  for (let y = 0; y < BOARD_SIZE; y += 1) {
    for (let x = 0; x < BOARD_SIZE; x += 1) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.setAttribute("role", "gridcell");
      cell.setAttribute("aria-label", `Column ${x + 1}, row ${y + 1}`);
      cell.innerHTML = entityMarkup(x, y);
      board.append(cell);
    }
  }

  energyValue.textContent = String(state.player.energy).padStart(2, "0");
  energyBar.style.width = `${(state.player.energy / MAX_ENERGY) * 100}%`;
  energyBar.classList.toggle("critical", state.player.energy <= 5);
  scoreValue.textContent = String(state.player.score).padStart(4, "0");
  movesValue.textContent = String(state.stats.moves).padStart(2, "0");
  statusMessage.textContent = state.message;
  seedValue.textContent = String(state.lifecycle.seed);
  directive.textContent = state.objective.exitUnlocked
    ? "Reach the uplink"
    : state.objective.nextRelay
      ? `Activate relay ${state.objective.nextRelay[0]!.toUpperCase()}`
      : "Restore the relay chain";
  progress.innerHTML = state.relays
    .map((relay) => `<span class="progress-node ${relay.active ? "active" : ""}">${relay.label}</span>`)
    .join("<i></i>");
  pauseButton.textContent = state.lifecycle.paused ? "▶" : "II";
  pauseButton.setAttribute("aria-label", state.lifecycle.paused ? "Resume game" : "Pause game");
  pauseButton.disabled = state.lifecycle.status !== "playing";

  overlay.innerHTML = overlayMarkup();
  overlay.classList.toggle("visible", overlay.innerHTML.length > 0);
  overlay.querySelector<HTMLButtonElement>("#primary-action")?.addEventListener("click", () => {
    if (state.lifecycle.status === "ready") dispatch({ name: "start" });
    else if (state.lifecycle.paused) dispatch({ name: "togglePause" });
    else dispatch({ name: "restart" });
  });
}

const keyDirections: Record<string, Direction | undefined> = {
  ArrowUp: "up", w: "up", W: "up",
  ArrowDown: "down", s: "down", S: "down",
  ArrowLeft: "left", a: "left", A: "left",
  ArrowRight: "right", d: "right", D: "right"
};

window.addEventListener("keydown", (event) => {
  const direction = keyDirections[event.key];
  if (direction) {
    event.preventDefault();
    dispatch({ name: "move", payload: { direction } });
    return;
  }
  if (event.key === "Enter" && state.lifecycle.status === "ready") dispatch({ name: "start" });
  if (event.key === "Escape") dispatch({ name: "togglePause" });
  if (event.key === "r" || event.key === "R") dispatch({ name: "restart" });
});

pauseButton.addEventListener("click", () => dispatch({ name: "togglePause" }));
document.querySelectorAll<HTMLButtonElement>("[data-direction]").forEach((button) => {
  button.addEventListener("click", () => dispatch({
    name: "move",
    payload: { direction: button.dataset.direction as Direction }
  }));
});

window.__WEB2D_GAME__ = {
  describe: () => ({
    protocolVersion: "1",
    name: "signal-relay",
    framework: "TypeScript + DOM/CSS",
    capabilities: ["state", "reset", "dispatch", "metrics"]
  }),
  getState: () => structuredClone(state) as unknown as Record<string, string | number | boolean | null | object>,
  reset: ({ seed } = {}) => {
    state = createInitialState(seed ?? 1);
    render();
  },
  dispatch: (action) => {
    if (action.name === "move") {
      const direction = (action.payload as { direction?: Direction } | undefined)?.direction;
      if (!direction || !["up", "down", "left", "right"].includes(direction)) throw new Error("move requires a valid direction");
      dispatch({ name: "move", payload: { direction } });
      return;
    }
    if (action.name === "start" || action.name === "togglePause") {
      dispatch({ name: action.name });
      return;
    }
    if (action.name === "restart") {
      const seed = (action.payload as { seed?: number } | undefined)?.seed;
      dispatch({ name: "restart", payload: { seed } });
      return;
    }
    throw new Error(`Unsupported action: ${action.name}`);
  },
  getMetrics: () => ({
    activeEntities: 1 + state.relays.length + state.hazards.length + Number(!state.charge.collected),
    moves: state.stats.moves,
    hazardHits: state.stats.hazardHits
  })
};

declare global {
  interface Window {
    __WEB2D_GAME__?: {
      describe(): { protocolVersion: "1"; name: string; framework: string; capabilities: string[] };
      getState(): Record<string, unknown>;
      reset(options?: { seed?: number }): void;
      dispatch(action: { name: string; payload?: unknown }): void;
      getMetrics(): Record<string, number>;
    };
  }
}

render();
