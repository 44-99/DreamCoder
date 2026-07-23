import type { AssertionResult, GameAssertion, GameState, JsonValue } from "../types.js";

const PATH_SEGMENT = /(?:^|\.)([^.[\]]+)|\[(\d+)\]/g;

export function readStatePath(state: GameState, path: string): JsonValue | undefined {
  if (!path.trim()) return state;

  const segments: Array<string | number> = [];
  let match: RegExpExecArray | null;
  while ((match = PATH_SEGMENT.exec(path)) !== null) {
    const property = match[1];
    const index = match[2];
    segments.push(index === undefined ? property! : Number(index));
  }

  if (segments.length === 0) return undefined;
  if (segments.some((segment) => typeof segment === "string" && ["__proto__", "prototype", "constructor"].includes(segment))) {
    return undefined;
  }
  let value: JsonValue | undefined = state;
  for (const segment of segments) {
    if (value === null || typeof value !== "object") return undefined;
    if (typeof segment === "number") {
      if (!Array.isArray(value)) return undefined;
      value = value[segment];
    } else {
      if (Array.isArray(value)) return undefined;
      value = value[segment];
    }
  }
  return value;
}

function equalJson(actual: JsonValue | undefined, expected: JsonValue | undefined): boolean {
  return JSON.stringify(actual) === JSON.stringify(expected);
}

function compareNumber(
  actual: JsonValue | undefined,
  expected: JsonValue | undefined,
  predicate: (left: number, right: number) => boolean
): boolean {
  return typeof actual === "number" && typeof expected === "number" && predicate(actual, expected);
}

export function evaluateAssertion(state: GameState, assertion: GameAssertion): AssertionResult {
  const actual = readStatePath(state, assertion.path);
  const expected = assertion.expected;
  let passed = false;

  switch (assertion.operator) {
    case "equals":
      passed = equalJson(actual, expected);
      break;
    case "notEquals":
      passed = !equalJson(actual, expected);
      break;
    case "greaterThan":
      passed = compareNumber(actual, expected, (left, right) => left > right);
      break;
    case "greaterThanOrEqual":
      passed = compareNumber(actual, expected, (left, right) => left >= right);
      break;
    case "lessThan":
      passed = compareNumber(actual, expected, (left, right) => left < right);
      break;
    case "lessThanOrEqual":
      passed = compareNumber(actual, expected, (left, right) => left <= right);
      break;
    case "includes":
      passed =
        (typeof actual === "string" && typeof expected === "string" && actual.includes(expected)) ||
        (Array.isArray(actual) && expected !== undefined && actual.some((item) => equalJson(item, expected)));
      break;
    case "exists":
      passed = expected === false ? actual === undefined : actual !== undefined;
      break;
  }

  const fallback = passed
    ? `${assertion.path} ${assertion.operator} assertion passed`
    : `${assertion.path} ${assertion.operator} assertion failed: expected ${JSON.stringify(expected)}, received ${JSON.stringify(actual)}`;

  return {
    assertion,
    ...(actual === undefined ? {} : { actual }),
    passed,
    message: assertion.message ?? fallback
  };
}

export function evaluateAssertions(state: GameState, assertions: GameAssertion[]): AssertionResult[] {
  return assertions.map((assertion) => evaluateAssertion(state, assertion));
}
