// Dev launcher: starts the FastAPI backend (uvicorn :8000) together with the
// Vite dev server, so `npm run dev` brings up the whole app. Extra CLI args
// (e.g. --host/--port from Kimi Work) are forwarded to Vite. If a backend is
// already listening on :8000 it is reused, not duplicated.
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const frontendDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const backendDir = path.resolve(frontendDir, "../backend");
const python = path.join(backendDir, ".venv", "Scripts", "python.exe");

const children = [];

function run(name, cmd, args, cwd) {
  const child = spawn(cmd, args, { cwd, stdio: ["ignore", "pipe", "pipe"], shell: false });
  const tag = (chunk) =>
    chunk
      .toString()
      .split(/\r?\n/)
      .filter(Boolean)
      .map((line) => `[${name}] ${line}`)
      .join("\n") + "\n";
  child.stdout.on("data", (d) => process.stdout.write(tag(d)));
  child.stderr.on("data", (d) => process.stderr.write(tag(d)));
  child.on("exit", (code) => {
    if (code) console.error(`[${name}] exited with code ${code}`);
  });
  children.push(child);
  return child;
}

async function backendUp() {
  try {
    const res = await fetch("http://localhost:8000/health", {
      signal: AbortSignal.timeout(1500),
    });
    return res.ok;
  } catch {
    return false;
  }
}

if (await backendUp()) {
  console.log("[dev] backend already running on :8000 — reusing it");
} else {
  run("api", python, ["-m", "uvicorn", "app.main:app", "--port", "8000"], backendDir);
}

run("web", process.execPath, [path.join(frontendDir, "node_modules", "vite", "bin", "vite.js"), ...process.argv.slice(2)], frontendDir);

function shutdown() {
  for (const child of children) {
    try {
      child.kill();
    } catch {
      // already gone
    }
  }
  process.exit(0);
}
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
process.on("exit", shutdown);
