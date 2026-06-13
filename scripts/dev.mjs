import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const isWindows = process.platform === "win32";
const pythonPath = join(
  root,
  "backend",
  ".venv",
  "Scripts",
  isWindows ? "python.exe" : "python",
);
const npmCommand = isWindows ? "npm.cmd" : "npm";

if (!existsSync(pythonPath)) {
  console.error("Backend virtual environment was not found at backend/.venv.");
  console.error("Create it first: cd backend && python -m venv .venv && pip install -r requirements.txt");
  process.exit(1);
}

const children = [
  start("api", pythonPath, ["-m", "uvicorn", "app.main:app", "--reload"], join(root, "backend")),
  start("web", npmCommand, ["--prefix", "frontend", "run", "dev"], root),
];

let shuttingDown = false;

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => shutdown(signal));
}

function start(name, command, args, cwd) {
  const child = spawn(command, args, {
    cwd,
    env: process.env,
    shell: isWindows,
  });

  child.stdout.on("data", (chunk) => write(name, chunk));
  child.stderr.on("data", (chunk) => write(name, chunk));
  child.on("exit", (code) => {
    if (!shuttingDown && code !== 0) {
      console.error(`[${name}] exited with code ${code}`);
      shutdown("SIGTERM");
    }
  });

  return child;
}

function write(name, chunk) {
  for (const line of chunk.toString().split(/\r?\n/)) {
    if (line.trim()) console.log(`[${name}] ${line}`);
  }
}

function shutdown(signal) {
  if (shuttingDown) return;
  shuttingDown = true;
  for (const child of children) {
    if (!child.killed) child.kill(signal);
  }
  setTimeout(() => process.exit(0), 300);
}
