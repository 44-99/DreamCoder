#!/usr/bin/env node
import { loadScenarioDocuments } from "./scenarios/schema.js";
import { formatScenarioSuite, runScenarioSuite } from "./scenarios/runner.js";

interface CliOptions {
  url: string;
  reporter: "text" | "json";
  paths: string[];
}

const HELP = `Usage:
  web2dkit run --url <http://game-url> [--reporter text|json] <scenario-or-directory...>

The game server must already be running. Web2DKit never executes project server commands.`;

function parseArguments(args: string[]): CliOptions | null {
  if (args.length === 0 || args.includes("--help") || args.includes("-h")) return null;
  if (args.shift() !== "run") throw new Error("The first argument must be `run`.");
  let url: string | undefined;
  let reporter: "text" | "json" = "text";
  const paths: string[] = [];
  while (args.length) {
    const value = args.shift()!;
    if (value === "--url") url = args.shift();
    else if (value === "--reporter") {
      const selected = args.shift();
      if (selected !== "text" && selected !== "json") throw new Error("--reporter must be text or json.");
      reporter = selected;
    } else if (value.startsWith("-")) throw new Error(`Unknown option: ${value}`);
    else paths.push(value);
  }
  if (!url) throw new Error("--url is required.");
  const parsedUrl = new URL(url);
  if (parsedUrl.protocol !== "http:" && parsedUrl.protocol !== "https:") throw new Error("--url must use http:// or https://.");
  if (paths.length === 0) throw new Error("At least one scenario file or directory is required.");
  return { url: parsedUrl.toString(), reporter, paths };
}

async function main(): Promise<void> {
  const options = parseArguments(process.argv.slice(2));
  if (!options) {
    console.log(HELP);
    return;
  }
  const scenarios = await loadScenarioDocuments(options.paths);
  const result = await runScenarioSuite({ url: options.url, scenarios });
  console.log(formatScenarioSuite(result, options.reporter));
  if (!result.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
