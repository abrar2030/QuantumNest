#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const binDir = path.join(__dirname, "..", "node_modules", ".bin");

function chmodExecutable(filePath) {
  try {
    const stat = fs.lstatSync(filePath);
    if (stat.isSymbolicLink()) {
      const resolved = fs.realpathSync(filePath);
      chmodExecutable(resolved);
      return;
    }
    if (stat.isFile()) {
      fs.chmodSync(filePath, stat.mode | 0o111);
    }
  } catch {
    // Best-effort only. Never fail the install because of this.
  }
}

if (process.platform !== "win32" && fs.existsSync(binDir)) {
  for (const entry of fs.readdirSync(binDir)) {
    chmodExecutable(path.join(binDir, entry));
  }
}
