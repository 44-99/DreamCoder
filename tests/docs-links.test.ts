import { access, readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";

async function markdownFiles(directory: string): Promise<string[]> {
  const files: string[] = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if ([".git", "node_modules", "dist"].includes(entry.name)) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await markdownFiles(absolute));
    else if (entry.isFile() && entry.name.endsWith(".md")) files.push(absolute);
  }
  return files;
}

describe("documentation routes", () => {
  it("keeps every relative Markdown link resolvable", async () => {
    const failures: string[] = [];
    for (const file of await markdownFiles(process.cwd())) {
      const markdown = await readFile(file, "utf8");
      for (const match of markdown.matchAll(/!?\[[^\]]*\]\(([^)]+)\)/g)) {
        const rawTarget = match[1]?.trim().replace(/^<|>$/g, "");
        if (!rawTarget || /^(https?:|mailto:|#)/.test(rawTarget)) continue;
        const target = decodeURIComponent(rawTarget.split("#", 1)[0]!);
        const resolved = path.resolve(path.dirname(file), target);
        try {
          await access(resolved);
        } catch {
          failures.push(`${path.relative(process.cwd(), file)} -> ${rawTarget}`);
        }
      }
    }
    expect(failures).toEqual([]);
  });
});
