/**
 * Test helpers for the BlackRoad OS validator/sync suite.
 *
 * The validators and sync scripts resolve every path from a single repo root.
 * Each script honours a BLACKROAD_ROOT env override (added for exactly this
 * purpose), so a test can copy the real Registry/ into a throwaway directory,
 * mutate one record, and run the real script against the copy — exercising the
 * actual CLI contract (exit code + messages), not a re-implementation of it.
 */
import { cpSync, mkdtempSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

export const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

/**
 * Create an isolated copy of the repo's registry data (and index.html) in a
 * temp dir. Returns handles to read/mutate registry files and run scripts
 * against the sandbox. Register `sandbox.cleanup` with `t.after`.
 */
export function makeSandbox({ withIndexHtml = false, withProducts = false } = {}) {
  const dir = mkdtempSync(join(tmpdir(), "blackroad-test-"));
  cpSync(join(REPO_ROOT, "Registry"), join(dir, "Registry"), { recursive: true });
  if (withIndexHtml) {
    cpSync(join(REPO_ROOT, "index.html"), join(dir, "index.html"));
  }
  if (withProducts) {
    cpSync(join(REPO_ROOT, "Products"), join(dir, "Products"), { recursive: true });
  }

  const regPath = (name) => join(dir, "Registry", name);

  return {
    dir,
    /** Parse a registry file from the sandbox. */
    read(name) {
      return JSON.parse(readFileSync(regPath(name), "utf8"));
    },
    /** Write a JS object back to a registry file in the sandbox. */
    write(name, obj) {
      writeFileSync(regPath(name), JSON.stringify(obj, null, 2));
    },
    /** Read/write a raw (non-JSON) sandbox file such as index.html. */
    readRaw(name) {
      return readFileSync(join(dir, name), "utf8");
    },
    writeRaw(name, contents) {
      writeFileSync(join(dir, name), contents);
    },
    /** Load a registry file, mutate it in place via `fn`, and write it back. */
    mutate(name, fn) {
      const obj = this.read(name);
      fn(obj);
      this.write(name, obj);
    },
    /** Run a script in scripts/ against this sandbox. Returns {code, stdout, stderr}. */
    run(script, args = []) {
      const res = spawnSync("node", [join(REPO_ROOT, "scripts", script), ...args], {
        env: { ...process.env, BLACKROAD_ROOT: dir },
        encoding: "utf8",
      });
      return { code: res.status, stdout: res.stdout ?? "", stderr: res.stderr ?? "" };
    },
    cleanup() {
      rmSync(dir, { recursive: true, force: true });
    },
  };
}
