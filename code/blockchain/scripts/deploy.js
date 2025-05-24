const { ethers } = require("ethers");
require('dotenv').config();

// Import contract artifacts
const TestToken = require('../artifacts/contracts/TestToken.sol/TestToken.json');
const TokenizedAsset = require('../artifacts/contracts/TokenizedAsset.sol/TokenizedAsset.json');
const PortfolioManager = require('../artifacts/contracts/PortfolioManager.sol/PortfolioManager.json');
const TradingPlatform = require('../artifacts/contracts/TradingPlatform.sol/TradingPlatform.json');
const DeFiIntegration = require('../artifacts/contracts/DeFiIntegration.sol/DeFiIntegration.json');

async function main() {
  // Get private key from environment variables
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    console.error("Please set your PRIVATE_KEY in a .env file");
    return;
  }

  // Get Infura API key from environment variables
  const infuraApiKey = process.env.INFURA_API_KEY;
  if (!infuraApiKey) {
    console.error("Please set your INFURA_API_KEY in a .env file");
    return;
  }

  // Connect to Goerli testnet
  const provider = new ethers.providers.InfuraProvider("goerli", infuraApiKey);
  const wallet = new ethers.Wallet(privateKey, provider);
  const deployer = wallet.address;

  console.log("Deploying contracts with the account:", deployer);
  console.log("Account balance:", (await provider.getBalance(deployer)).toString());

  try {
    // Deploy TestToken
    console.log("Deploying TestToken...");
    const testTokenFactory = new ethers.ContractFactory(
      TestToken.abi,
      TestToken.bytecode,
      wallet
    );
    const testToken = await testTokenFactory.deploy();
    await testToken.deployed();
    console.log("TestToken deployed to:", testToken.address);

    // Deploy TokenizedAsset
    console.log("Deploying TokenizedAsset...");
    const tokenizedAssetFactory = new ethers.ContractFactory(
      TokenizedAsset.abi,
      TokenizedAsset.bytecode,
      wallet
    );
    const tokenizedAsset = await tokenizedAssetFactory.deploy(
      "QuantumNest Apple Stock Token",
      "qAAPL",
      "AAPL",
      "Apple Inc.",
      "stock",
      1000000,
      17500, // $175.00
      "Tokenized representation of Apple Inc. stock",
      "QuantumNest Capital"
    );
    await tokenizedAsset.deployed();
    console.log("TokenizedAsset deployed to:", tokenizedAsset.address);

    // Deploy PortfolioManager
    console.log("Deploying PortfolioManager...");
    const portfolioManagerFactory = new ethers.ContractFactory(
      PortfolioManager.abi,
      PortfolioManager.bytecode,
      wallet
    );
    const portfolioManager = await portfolioManagerFactory.deploy();
    await portfolioManager.deployed();
    console.log("PortfolioManager deployed to:", portfolioManager.address);

    // Deploy TradingPlatform
    console.log("Deploying TradingPlatform...");
    const tradingPlatformFactory = new ethers.ContractFactory(
      TradingPlatform.abi,
      TradingPlatform.bytecode,
      wallet
    );
    const tradingPlatform = await tradingPlatformFactory.deploy(
      25, // 0.25% trading fee
      deployer // Fee collector
    );
    await tradingPlatform.deployed();
    console.log("TradingPlatform deployed to:", tradingPlatform.address);

    // Deploy DeFiIntegration
    console.log("Deploying DeFiIntegration...");
    const defiIntegrationFactory = new ethers.ContractFactory(
      DeFiIntegration.abi,
      DeFiIntegration.bytecode,
      wallet
    );
    const defiIntegration = await defiIntegrationFactory.deploy(
      20, // 0.20% platform fee
      deployer // Fee collector
    );
    await defiIntegration.deployed();
    console.log("DeFiIntegration deployed to:", defiIntegration.address);

    // Test interactions with deployed contracts
    console.log("\nTesting contract interactions...");

    // Test TokenizedAsset
    console.log("\nTesting TokenizedAsset...");
    console.log("Setting trading enabled...");
    await tokenizedAsset.setTradingEnabled(true);
    console.log("Updating asset value...");
    await tokenizedAsset.updateAssetValue(18000); // $180.00
    console.log("Updating performance...");
    await tokenizedAsset.updatePerformance(250); // 2.5% YTD return

    // Test PortfolioManager
    console.log("\nTesting PortfolioManager...");
    console.log("Creating portfolio...");
    const createPortfolioTx = await portfolioManager.createPortfolio(
      "Growth Portfolio",
      "High-growth technology stocks"
    );
    const createPortfolioReceipt = await createPortfolioTx.wait();
    // Get portfolio ID from event logs
    const portfolioCreatedEvent = createPortfolioReceipt.events.find(
      event => event.event === "PortfolioCreated"
    );
    const portfolioId = portfolioCreatedEvent.args.portfolioId;
    console.log(`Portfolio created with ID: ${portfolioId}`);

    console.log("Adding asset to portfolio...");
    await portfolioManager.addAsset(
      portfolioId,
      tokenizedAsset.address,
      "qAAPL",
      5000 // 50% allocation
    );

    // Test TradingPlatform
    console.log("\nTesting TradingPlatform...");
    console.log("Whitelisting token...");
    await tradingPlatform.whitelistToken(tokenizedAsset.address);
    console.log("Enabling trading...");
    await tradingPlatform.setTradingEnabled(true);

    // Test DeFiIntegration
    console.log("\nTesting DeFiIntegration...");
    console.log("Creating investment strategy...");
    await defiIntegration.createStrategy(
      "Staking Strategy",
      "Earn yield by staking tokens",
      deployer, // Mock protocol address
      "QuantumNest Staking",
      testToken.address,
      "QNT",
      500, // 5% APY
      2, // Risk level 2 (low-moderate)
      2592000, // 30-day lock period
      100 * 10**18, // 100 tokens minimum
      0 // No maximum
    );
    console.log("Enabling investments...");
    await defiIntegration.setInvestmentsEnabled(true);

    console.log("\nAll contracts deployed and tested successfully!");
    
    // Save deployment addresses to a file
    const fs = require('fs');
    const deploymentInfo = {
      network: "goerli",
      testToken: testToken.address,
      tokenizedAsset: tokenizedAsset.address,
      portfolioManager: portfolioManager.address,
      tradingPlatform: tradingPlatform.address,
      defiIntegration: defiIntegration.address,
      deployer: deployer,
      timestamp: new Date().toISOString()
    };
    
    fs.writeFileSync(
      'deployment.json',
      JSON.stringify(deploymentInfo, null, 2)
    );
    console.log("\nDeployment information saved to deployment.json");

  } catch (error) {
    console.error("Deployment failed:", error);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
