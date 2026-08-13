const { expect } = require("chai");
const { ethers } = require("hardhat");
const { anyValue } = require("@nomicfoundation/hardhat-chai-matchers/withArgs");

async function deployAsset() {
  const [owner, alice, bob] = await ethers.getSigners();
  const TokenizedAsset = await ethers.getContractFactory("TokenizedAsset");
  const asset = await TokenizedAsset.deploy(
    "QuantumNest Apple Stock Token",
    "qAAPL",
    "AAPL",
    "Apple Inc.",
    "stock",
    1000000, // initial supply (whole tokens)
    17500, // $175.00 in cents
    "Tokenized representation of Apple Inc. stock",
    "QuantumNest Capital",
  );
  await asset.deployed();
  return { asset, owner, alice, bob };
}

describe("TokenizedAsset", function () {
  describe("Deployment", function () {
    it("sets asset metadata correctly", async function () {
      const { asset } = await deployAsset();
      const details = await asset.getAssetDetails();

      expect(details._assetSymbol).to.equal("AAPL");
      expect(details._assetName).to.equal("Apple Inc.");
      expect(details._assetType).to.equal("stock");
      expect(details._assetValue).to.equal(17500);
      expect(details._issuer).to.equal("QuantumNest Capital");
      expect(details._tradingEnabled).to.equal(false);
      expect(details._tradingFee).to.equal(25);
    });

    it("mints the initial supply to the deployer", async function () {
      const { asset, owner } = await deployAsset();
      expect(await asset.balanceOf(owner.address)).to.equal(
        ethers.utils.parseEther("1000000"),
      );
    });
  });

  describe("Admin controls", function () {
    it("lets the owner update asset value and emits AssetRevalued", async function () {
      const { asset } = await deployAsset();
      await expect(asset.updateAssetValue(18000))
        .to.emit(asset, "AssetRevalued")
        .withArgs(17500, 18000, anyValue);
      expect(await asset.assetValue()).to.equal(18000);
    });

    it("lets the owner update performance", async function () {
      const { asset } = await deployAsset();
      await expect(asset.updatePerformance(250)).to.emit(
        asset,
        "PerformanceUpdated",
      );
      expect(await asset.yearToDateReturn()).to.equal(250);
    });

    it("rejects a trading fee above the 5% cap", async function () {
      const { asset } = await deployAsset();
      await expect(asset.setTradingFee(501)).to.be.revertedWith("Fee too high");
    });

    it("lets the owner update metadata", async function () {
      const { asset } = await deployAsset();
      await asset.updateMetadata("Updated description", 1893456000);
      expect(await asset.description()).to.equal("Updated description");
      expect(await asset.maturityDate()).to.equal(1893456000);
    });

    it("allows a trading fee at exactly the 5% cap", async function () {
      const { asset } = await deployAsset();
      await expect(asset.setTradingFee(500)).to.not.be.reverted;
      expect(await asset.tradingFee()).to.equal(500);
    });

    it("reverts admin functions for non-owners", async function () {
      const { asset, alice } = await deployAsset();
      await expect(
        asset.connect(alice).updateAssetValue(1),
      ).to.be.revertedWithCustomError(asset, "OwnableUnauthorizedAccount");
    });
  });

  describe("Trading restrictions", function () {
    it("blocks transfers between non-owner accounts while trading is disabled", async function () {
      const { asset, owner, alice, bob } = await deployAsset();
      await asset.transfer(alice.address, ethers.utils.parseEther("100"));

      await expect(
        asset
          .connect(alice)
          .transfer(bob.address, ethers.utils.parseEther("10")),
      ).to.be.revertedWith("Trading not enabled");
    });

    it("allows the owner to send/receive tokens even while trading is disabled", async function () {
      const { asset, owner, alice } = await deployAsset();
      await expect(
        asset.transfer(alice.address, ethers.utils.parseEther("100")),
      ).to.not.be.reverted;
      expect(await asset.balanceOf(alice.address)).to.equal(
        ethers.utils.parseEther("100"),
      );
    });

    it("charges the trading fee to the owner once trading is enabled", async function () {
      const { asset, owner, alice, bob } = await deployAsset();
      await asset.transfer(alice.address, ethers.utils.parseEther("1000"));
      await asset.setTradingEnabled(true);

      const sendAmount = ethers.utils.parseEther("100");
      const expectedFee = sendAmount.mul(25).div(10000); // 0.25%

      await asset.connect(alice).transfer(bob.address, sendAmount);

      expect(await asset.balanceOf(bob.address)).to.equal(
        sendAmount.sub(expectedFee),
      );
      expect(await asset.balanceOf(owner.address)).to.equal(
        ethers.utils.parseEther("999000").add(expectedFee),
      );
    });

    it("does not require trading to be enabled for minting or burning", async function () {
      const { asset, alice } = await deployAsset();
      // trading is disabled by default
      await expect(asset.mint(alice.address, ethers.utils.parseEther("5"))).to
        .not.be.reverted;
      expect(await asset.balanceOf(alice.address)).to.equal(
        ethers.utils.parseEther("5"),
      );

      await expect(asset.connect(alice).burn(ethers.utils.parseEther("5"))).to
        .not.be.reverted;
      expect(await asset.balanceOf(alice.address)).to.equal(0);
    });
  });
});
