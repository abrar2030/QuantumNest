const fs = require("fs");
const path = require("path");
const hre = require("hardhat");

/**
 * Extracts lean ABI-only JSON files (just { contractName, abi }) from the
 * full Hardhat build artifacts and writes them to deployments/abis/.
 *
 * Other services (e.g. the Python backend) that need to call these
 * contracts via web3 shouldn't have to depend on a Solidity toolchain or
 * parse Hardhat's much larger build-info files - they just need the ABI.
 * This keeps that hand-off explicit and versioned alongside deployments/.
 *
 * Usage:
 *   npx hardhat run scripts/export-abis.js
 *
 * Also invoked automatically at the end of scripts/deploy.js so the ABI
 * bundle and the deployed addresses always stay in sync.
 */
const CONTRACT_NAMES = [
  "TestToken",
  "TokenizedAsset",
  "PortfolioManager",
  "TradingPlatform",
  "DeFiIntegration",
];

async function exportAbis() {
  const outDir = path.join(__dirname, "..", "deployments", "abis");
  fs.mkdirSync(outDir, { recursive: true });

  for (const name of CONTRACT_NAMES) {
    const artifact = await hre.artifacts.readArtifact(name);
    const lean = {
      contractName: artifact.contractName,
      abi: artifact.abi,
      // Included (not just the ABI) so the backend can deploy *new*
      // instances of these known contract types via
      // POST /blockchain/deploy/contract without needing its own copy of
      // the Solidity toolchain.
      bytecode: artifact.bytecode,
    };
    const outPath = path.join(outDir, `${name}.json`);
    fs.writeFileSync(outPath, JSON.stringify(lean, null, 2));
    console.log(`Exported ABI: ${outPath}`);
  }

  return outDir;
}

module.exports = { exportAbis, CONTRACT_NAMES };

if (require.main === module) {
  exportAbis()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error("ABI export failed:", error);
      process.exit(1);
    });
}
