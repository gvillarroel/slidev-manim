import { readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const budget = 15;
const ignored = new Set([]);

const entries = readdirSync(repoRoot, { withFileTypes: true })
  .map((entry) => entry.name)
  .filter((name) => !ignored.has(name))
  .sort((left, right) => left.localeCompare(right));

if (entries.length > budget) {
  console.error(`Root entry budget exceeded: ${entries.length}/${budget}`);
  for (const entry of entries) {
    console.error(`- ${entry}`);
  }
  process.exit(1);
}

console.log(`Root entry budget OK: ${entries.length}/${budget}`);
for (const entry of entries) {
  console.log(`- ${entry}`);
}
