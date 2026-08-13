require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();
const { subtask } = require("hardhat/config");
const {
  TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD,
} = require("hardhat/builtin-tasks/task-names");

const SOLC_VERSION = "0.8.20";

// Hardhat normally downloads the solc binary/wasm build it needs from
// https://binaries.soliditylang.org on every fresh machine/CI run. That
// endpoint is unreachable in locked-down/offline environments (corporate
// proxies, sandboxed CI, air-gapped builds), which makes `hardhat compile`
// fail with HH502 even though nothing is wrong with the contracts.
//
// To make builds hermetic we ship the exact matching compiler as the
// `solc` npm package (see package.json dependencies) and point Hardhat
// at its bundled soljson.js instead of downloading it. If that package
// isn't installed for some reason, we transparently fall back to
// Hardhat's normal download behavior.
subtask(TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD).setAction(
  async (args, _hre, runSuper) => {
    if (args.solcVersion === SOLC_VERSION) {
      try {
        const solcJsPath = require.resolve("solc/soljson.js");
        return {
          compilerPath: solcJsPath,
          isSolcJs: true,
          version: args.solcVersion,
          longVersion: `${args.solcVersion}+commit.local`,
        };
      } catch (e) {
        // local solc package not available, fall through to default
      }
    }
    return runSuper(args);
  },
);

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const INFURA_API_KEY = process.env.INFURA_API_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      // solidity-coverage instruments contracts with extra bookkeeping
      // and compiles with the optimizer effectively off, which pushes a
      // couple of functions (e.g. TradingPlatform.executeTrade,
      // DeFiIntegration.createInvestment) past the EVM's 16-local-variable
      // stack limit ("stack too deep"). Routing compilation through the
      // IR pipeline avoids that without changing contract behavior.
      viaIR: true,
    },
  },
  networks: {
    // Local Hardhat node (default)
    hardhat: {
      chainId: 31337,
      mining: {
        auto: true,
        interval: 0,
      },
    },
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },
    // Used inside docker-compose, where the Hardhat node runs as the
    // `blockchain` service rather than on localhost. See
    // ../docker-compose.yml (services: blockchain, blockchain-deploy).
    docker: {
      url: process.env.HARDHAT_NETWORK_RPC_URL || "http://blockchain:8545",
      chainId: 31337,
    },
    // Testnets (require INFURA_API_KEY + PRIVATE_KEY)
    // NOTE: Goerli and Mumbai were deprecated and are no longer reliably
    // available; Sepolia (Ethereum) and Amoy (Polygon) are their official
    // replacements.
    sepolia: {
      url: INFURA_API_KEY
        ? `https://sepolia.infura.io/v3/${INFURA_API_KEY}`
        : "https://rpc.ankr.com/eth_sepolia",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 11155111,
    },
    polygon_amoy: {
      url: INFURA_API_KEY
        ? `https://polygon-amoy.infura.io/v3/${INFURA_API_KEY}`
        : "https://rpc.ankr.com/polygon_amoy",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 80002,
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY || "",
  },
  paths: {
    artifacts: "./artifacts",
    cache: "./cache",
    sources: "./contracts",
    tests: "./test",
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS !== undefined,
    currency: "USD",
  },
};
