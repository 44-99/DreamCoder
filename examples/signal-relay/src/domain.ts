export type Direction = "up" | "down" | "left" | "right";
export type GameStatus = "ready" | "playing" | "won" | "lost";

export interface Position {
  x: number;
  y: number;
}

export interface Relay extends Position {
  id: "alpha" | "beta" | "gamma";
  label: "A" | "B" | "C";
  order: number;
  active: boolean;
}

export interface GameState {
  scene: "relay-field";
  lifecycle: {
    status: GameStatus;
    paused: boolean;
    seed: number;
    turn: number;
  };
  player: {
    position: Position;
    energy: number;
    score: number;
  };
  objective: {
    relaysActivated: number;
    totalRelays: 3;
    nextRelay: Relay["id"] | null;
    exitUnlocked: boolean;
  };
  relays: Relay[];
  hazards: Array<Position & { id: string }>;
  charge: Position & { id: string; collected: boolean };
  exit: Position;
  stats: {
    moves: number;
    hazardHits: number;
  };
  message: string;
}

export type DomainAction =
  | { name: "start" }
  | { name: "move"; payload: { direction: Direction } }
  | { name: "togglePause" }
  | { name: "restart"; payload?: { seed?: number } };

export const BOARD_SIZE = 7;
export const MAX_ENERGY = 18;

const RELAY_LAYOUT: ReadonlyArray<Omit<Relay, "active">> = [
  { id: "alpha", label: "A", order: 0, x: 1, y: 1 },
  { id: "beta", label: "B", order: 1, x: 5, y: 1 },
  { id: "gamma", label: "C", order: 2, x: 5, y: 5 }
];

const HAZARD_LAYOUT = [
  { id: "hazard-north", x: 3, y: 2 },
  { id: "hazard-core", x: 2, y: 3 },
  { id: "hazard-south", x: 3, y: 5 }
] as const;

const CHARGE_CANDIDATES: Position[] = [
  { x: 0, y: 3 },
  { x: 4, y: 4 },
  { x: 6, y: 3 }
];

function seededIndex(seed: number, length: number): number {
  let value = seed >>> 0;
  value ^= value << 13;
  value ^= value >>> 17;
  value ^= value << 5;
  return (value >>> 0) % length;
}

export function createInitialState(seed = 1): GameState {
  const charge = CHARGE_CANDIDATES[seededIndex(seed, CHARGE_CANDIDATES.length)]!;
  return {
    scene: "relay-field",
    lifecycle: { status: "ready", paused: false, seed: seed >>> 0, turn: 0 },
    player: { position: { x: 0, y: 0 }, energy: MAX_ENERGY, score: 0 },
    objective: { relaysActivated: 0, totalRelays: 3, nextRelay: "alpha", exitUnlocked: false },
    relays: RELAY_LAYOUT.map((relay) => ({ ...relay, active: false })),
    hazards: HAZARD_LAYOUT.map((hazard) => ({ ...hazard })),
    charge: { id: `charge-${charge.x}-${charge.y}`, ...charge, collected: false },
    exit: { x: 0, y: 6 },
    stats: { moves: 0, hazardHits: 0 },
    message: "Press Enter or select Begin mission."
  };
}

function samePosition(a: Position, b: Position): boolean {
  return a.x === b.x && a.y === b.y;
}

function nextPosition(position: Position, direction: Direction): Position {
  const offsets: Record<Direction, Position> = {
    up: { x: 0, y: -1 },
    down: { x: 0, y: 1 },
    left: { x: -1, y: 0 },
    right: { x: 1, y: 0 }
  };
  return { x: position.x + offsets[direction].x, y: position.y + offsets[direction].y };
}

function isInsideBoard(position: Position): boolean {
  return position.x >= 0 && position.y >= 0 && position.x < BOARD_SIZE && position.y < BOARD_SIZE;
}

export function applyAction(current: GameState, action: DomainAction): GameState {
  if (action.name === "restart") {
    return createInitialState(action.payload?.seed ?? current.lifecycle.seed);
  }

  const state = structuredClone(current);

  if (action.name === "start") {
    if (state.lifecycle.status === "ready") {
      state.lifecycle.status = "playing";
      state.message = "Relay A is awaiting your signal.";
    }
    return state;
  }

  if (action.name === "togglePause") {
    if (state.lifecycle.status === "playing") {
      state.lifecycle.paused = !state.lifecycle.paused;
      state.message = state.lifecycle.paused ? "Mission suspended." : "Mission resumed.";
    }
    return state;
  }

  if (action.name !== "move" || state.lifecycle.status !== "playing" || state.lifecycle.paused) {
    return state;
  }

  const destination = nextPosition(state.player.position, action.payload.direction);
  if (!isInsideBoard(destination)) {
    state.message = "Sector boundary reached. No energy spent.";
    return state;
  }

  state.player.position = destination;
  state.player.energy -= 1;
  state.lifecycle.turn += 1;
  state.stats.moves += 1;
  state.message = "Signal stable. Continue the route.";

  if (state.hazards.some((hazard) => samePosition(hazard, destination))) {
    state.player.energy -= 2;
    state.player.score = Math.max(0, state.player.score - 25);
    state.stats.hazardHits += 1;
    state.message = "Interference hit: two additional energy lost.";
  }

  if (!state.charge.collected && samePosition(state.charge, destination)) {
    state.charge.collected = true;
    state.player.energy = Math.min(MAX_ENERGY, state.player.energy + 3);
    state.player.score += 25;
    state.message = "Charge recovered: energy restored.";
  }

  const relay = state.relays.find((candidate) => samePosition(candidate, destination));
  if (relay && !relay.active) {
    if (relay.order === state.objective.relaysActivated) {
      relay.active = true;
      state.objective.relaysActivated += 1;
      state.player.score += 100;
      state.objective.nextRelay = state.relays[state.objective.relaysActivated]?.id ?? null;
      state.objective.exitUnlocked = state.objective.relaysActivated === state.objective.totalRelays;
      state.message = state.objective.exitUnlocked
        ? "Relay chain restored. Reach the uplink."
        : `Relay ${relay.label} online. Proceed to ${state.relays[state.objective.relaysActivated]!.label}.`;
    } else {
      state.message = `Relay ${relay.label} is out of sequence.`;
    }
  }

  if (samePosition(state.exit, destination)) {
    if (state.objective.exitUnlocked) {
      state.lifecycle.status = "won";
      state.player.score += 250 + state.player.energy * 10;
      state.message = "Transmission complete. Sector restored.";
    } else {
      state.message = "Uplink locked. Restore every relay first.";
    }
  }

  if (state.player.energy <= 0 && state.lifecycle.status !== "won") {
    state.player.energy = 0;
    state.lifecycle.status = "lost";
    state.message = "Courier power depleted. Restart the mission.";
  }

  return state;
}
