const fs = require("fs");
const path = require("path");
const hre = require("hardhat");
const { ethers } = hre;
const { exportAbis } = require("./export-abis");

/**
 * Deploys the full QuantumNest contract suite and wires them together with
 * a short smoke-test sequence.
 *
 * Network is selected via Hardhat's `--network` flag (e.g. `hardhat`,
 * `localhost`, `docker`, `sepolia`, `polygon_amoy`), not hardcoded here.
 * For any network other than the built-in `hardhat` in-process network,
 * make sure PRIVATE_KEY (and INFURA_API_KEY, if using the default Infura
 * RPC URLs) are set in your .env file - see hardhat.config.js.
 *
 * On success this writes:
 *   - deployments/<network>.json   (deployed contract addresses + chainId)
 *   - deployments/abis/*.json      (ABI for each contract, via export-abis.js)
 *
 * which is how the backend (see backend/app/services/blockchain_service.py)
 * discovers what to talk to, instead of hardcoding addresses.
 *
 * Usage:
 *   npx hardhat run scripts/deploy.js --network localhost
 *   npx hardhat run scripts/deploy.js --network sepolia
 */
async function main() {
  const [deployer] = await ethers.getSigners();
  const deployerAddress = await deployer.getAddress();

  console.log("Network:", hre.network.name);
  console.log("Deploying contracts with the account:", deployerAddress);
  console.log(
    "Account balance:",
    (await ethers.provider.getBalance(deployerAddress)).toString(),
  );

  // Deploy TestToken (also used as the payment/settlement token for
  // TradingPlatform, standing in for a stablecoin in this demo deployment)
  console.log("\nDeploying TestToken...");
  const TestToken = await ethers.getContractFactory("TestToken");
  const testToken = await TestToken.deploy();
  await testToken.deployed();
  console.log("TestToken deployed to:", testToken.address);

  // Deploy TokenizedAsset
  console.log("\nDeploying TokenizedAsset...");
  const TokenizedAsset = await ethers.getContractFactory("TokenizedAsset");
  const tokenizedAsset = await TokenizedAsset.deploy(
    "QuantumNest Apple Stock Token",
    "qAAPL",
    "AAPL",
    "Apple Inc.",
    "stock",
    1000000,
    17500, // $175.00
    "Tokenized representation of Apple Inc. stock",
    "QuantumNest Capital",
  );
  await tokenizedAsset.deployed();
  console.log("TokenizedAsset deployed to:", tokenizedAsset.address);

  // Deploy PortfolioManager
  console.log("\nDeploying PortfolioManager...");
  const PortfolioManager = await ethers.getContractFactory("PortfolioManager");
  const portfolioManager = await PortfolioManager.deploy();
  await portfolioManager.deployed();
  console.log("PortfolioManager deployed to:", portfolioManager.address);

  // Deploy TradingPlatform
  console.log("\nDeploying TradingPlatform...");
  const TradingPlatform = await ethers.getContractFactory("TradingPlatform");
  const tradingPlatform = await TradingPlatform.deploy(
    25, // 0.25% trading fee
    deployerAddress, // Fee collector
    testToken.address, // Payment/settlement token
  );
  await tradingPlatform.deployed();
  console.log("TradingPlatform deployed to:", tradingPlatform.address);

  // Deploy DeFiIntegration
  console.log("\nDeploying DeFiIntegration...");
  const DeFiIntegration = await ethers.getContractFactory("DeFiIntegration");
  const defiIntegration = await DeFiIntegration.deploy(
    20, // 0.20% platform fee
    deployerAddress, // Fee collector
  );
  await defiIntegration.deployed();
  console.log("DeFiIntegration deployed to:", defiIntegration.address);

  // Wire the contracts together with a short smoke-test sequence
  console.log("\nTesting contract interactions...");

  console.log("\nTesting TokenizedAsset...");
  await (await tokenizedAsset.setTradingEnabled(true)).wait();
  await (await tokenizedAsset.updateAssetValue(18000)).wait(); // $180.00
  await (await tokenizedAsset.updatePerformance(250)).wait(); // 2.5% YTD

  console.log("\nTesting PortfolioManager...");
  const createPortfolioTx = await portfolioManager.createPortfolio(
    "Growth Portfolio",
    "High-growth technology stocks",
  );
  const createPortfolioReceipt = await createPortfolioTx.wait();
  const portfolioCreatedEvent = createPortfolioReceipt.events.find(
    (event) => event.event === "PortfolioCreated",
  );
  const portfolioId = portfolioCreatedEvent.args.portfolioId;
  console.log(`Portfolio created with ID: ${portfolioId}`);

  await (
    await portfolioManager.addAsset(
      portfolioId,
      tokenizedAsset.address,
      "qAAPL",
      5000, // 50% allocation
    )
  ).wait();

  console.log("\nTesting TradingPlatform...");
  await (await tradingPlatform.whitelistToken(tokenizedAsset.address)).wait();
  await (await tradingPlatform.setTradingEnabled(true)).wait();

  console.log("\nTesting DeFiIntegration...");
  await (
    await defiIntegration.createStrategy(
      "Staking Strategy",
      "Earn yield by staking tokens",
      deployerAddress, // Mock protocol address
      "QuantumNest Staking",
      testToken.address,
      "QNT",
      500, // 5% APY
      2, // Risk level 2 (low-moderate)
      2592000, // 30-day lock period
      ethers.utils.parseEther("100"), // 100 tokens minimum
      0, // No maximum
    )
  ).wait();
  await (await defiIntegration.setInvestmentsEnabled(true)).wait();

  console.log("\nAll contracts deployed and tested successfully!");

  // Persist deployment addresses, keyed by network, so other services
  // (e.g. the backend) can discover them without hardcoding addresses.
  // See deployments/README.md for the on-disk layout.
  const chainId = Number((await ethers.provider.getNetwork()).chainId);
  const deploymentInfo = {
    network: hre.network.name,
    chainId,
    contracts: {
      TestToken: testToken.address,
      TokenizedAsset: tokenizedAsset.address,
      PortfolioManager: portfolioManager.address,
      TradingPlatform: tradingPlatform.address,
      DeFiIntegration: defiIntegration.address,
    },
    deployer: deployerAddress,
    timestamp: new Date().toISOString(),
  };

  const deploymentsDir = path.join(__dirname, "..", "deployments");
  fs.mkdirSync(deploymentsDir, { recursive: true });
  const deploymentPath = path.join(deploymentsDir, `${hre.network.name}.json`);
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`\nDeployment addresses saved to ${deploymentPath}`);

  // Keep the ABI bundle in sync with what was just deployed.
  await exportAbis();
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });
