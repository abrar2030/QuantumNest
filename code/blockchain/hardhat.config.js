require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const PRIVATE_KEY =
  process.env.PRIVATE_KEY ||
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"; // default Hardhat account #0
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
    // Testnets (require INFURA_API_KEY + PRIVATE_KEY)
    goerli: {
      url: INFURA_API_KEY
        ? `https://goerli.infura.io/v3/${INFURA_API_KEY}`
        : "https://rpc.ankr.com/eth_goerli",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 5,
    },
    polygon_mumbai: {
      url: INFURA_API_KEY
        ? `https://polygon-mumbai.infura.io/v3/${INFURA_API_KEY}`
        : "https://rpc.ankr.com/polygon_mumbai",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 80001,
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
