#!/usr/bin/env node
/**
 * Restores the executable bit on everything in node_modules/.bin.
 *
 * Why this exists: on WSL, when a project lives on a Windows-mounted drive
 * (e.g. /mnt/c/Users/.../OneDrive/Desktop/...), the DrvFs filesystem and/or
 * OneDrive's sync process can silently strip the Unix executable permission
 * from files after `npm install`. The symlinks in node_modules/.bin still
 * point at the right files, but the target scripts (like next/dist/bin/next)
 * end up non-executable, which surfaces as:
 *
 *   sh: 1: next: Permission denied
 *
 * This is a no-op on Windows (no POSIX permission bits to fix) and a no-op
 * on a native Linux/macOS filesystem (bits are already correct), so it is
 * safe to run unconditionally on every install.
 */
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
