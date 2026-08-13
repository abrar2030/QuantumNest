const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

const PLATFORM_FEE_BPS = 20; // 0.20%
const LOCK_PERIOD = 30 * 24 * 60 * 60; // 30 days

describe("DeFiIntegration", function () {
  let defi, assetToken;
  let owner, feeCollector, alice, protocolStub;

  beforeEach(async function () {
    [owner, feeCollector, alice, protocolStub] = await ethers.getSigners();

    const TestToken = await ethers.getContractFactory("TestToken");
    assetToken = await TestToken.deploy();
    await assetToken.deployed();

    const DeFiIntegration = await ethers.getContractFactory("DeFiIntegration");
    defi = await DeFiIntegration.deploy(PLATFORM_FEE_BPS, feeCollector.address);
    await defi.deployed();

    await defi.setInvestmentsEnabled(true);

    await assetToken.transfer(alice.address, ethers.utils.parseEther("10000"));
    await assetToken
      .connect(alice)
      .approve(defi.address, ethers.constants.MaxUint256);
  });

  async function createStrategy(overrides = {}) {
    const params = Object.assign(
      {
        name: "Staking Strategy",
        description: "Earn yield by staking",
        protocolAddress: protocolStub.address,
        protocolName: "QuantumNest Staking",
        assetAddress: assetToken.address,
        assetSymbol: "QNT",
        apy: 500,
        risk: 2,
        lockPeriod: LOCK_PERIOD,
        minInvestment: ethers.utils.parseEther("100"),
        maxInvestment: 0,
      },
      overrides,
    );

    const tx = await defi.createStrategy(
      params.name,
      params.description,
      params.protocolAddress,
      params.protocolName,
      params.assetAddress,
      params.assetSymbol,
      params.apy,
      params.risk,
      params.lockPeriod,
      params.minInvestment,
      params.maxInvestment,
    );
    const receipt = await tx.wait();
    const event = receipt.events.find((e) => e.event === "StrategyCreated");
    return event.args.strategyId;
  }

  describe("createStrategy", function () {
    it("rejects an invalid risk level", async function () {
      await expect(createStrategy({ risk: 0 })).to.be.revertedWith(
        "Invalid risk level",
      );
      await expect(createStrategy({ risk: 6 })).to.be.revertedWith(
        "Invalid risk level",
      );
    });

    it("rejects a zero asset address", async function () {
      await expect(
        createStrategy({ assetAddress: ethers.constants.AddressZero }),
      ).to.be.revertedWith("Invalid asset address");
    });

    it("restricts strategy creation to the owner", async function () {
      const DeFiIntegration =
        await ethers.getContractFactory("DeFiIntegration");
      await expect(
        defi
          .connect(alice)
          .createStrategy(
            "x",
            "y",
            protocolStub.address,
            "z",
            assetToken.address,
            "QNT",
            500,
            2,
            LOCK_PERIOD,
            0,
            0,
          ),
      ).to.be.revertedWithCustomError(defi, "OwnableUnauthorizedAccount");
    });

    it("lets the owner update a strategy's terms", async function () {
      const strategyId = await createStrategy();
      await expect(
        defi.updateStrategy(
          strategyId,
          "Updated Strategy",
          "Updated description",
          800,
          3,
          LOCK_PERIOD * 2,
          ethers.utils.parseEther("200"),
          ethers.utils.parseEther("5000"),
        ),
      )
        .to.emit(defi, "StrategyUpdated")
        .withArgs(strategyId, "Updated Strategy", assetToken.address, 800, 3);

      const strategy = await defi.strategies(strategyId);
      expect(strategy.apy).to.equal(800);
      expect(strategy.risk).to.equal(3);
    });

    it("lets the owner deactivate a strategy, blocking new investments", async function () {
      const strategyId = await createStrategy();
      await expect(defi.deactivateStrategy(strategyId))
        .to.emit(defi, "StrategyDeactivated")
        .withArgs(strategyId);

      await expect(
        defi
          .connect(alice)
          .createInvestment(strategyId, ethers.utils.parseEther("1000")),
      ).to.be.revertedWith("Strategy not active");
    });

    it("returns active strategies via getActiveStrategies", async function () {
      const strategyId = await createStrategy();
      const active = await defi.getActiveStrategies(0, 10);
      expect(active.map((s) => s.id.toString())).to.include(
        strategyId.toString(),
      );
    });
  });

  describe("createInvestment", function () {
    it("deducts the platform fee and forwards it to the fee collector", async function () {
      const strategyId = await createStrategy();
      const amount = ethers.utils.parseEther("1000");
      const fee = amount.mul(PLATFORM_FEE_BPS).div(10000);

      const tx = await defi.connect(alice).createInvestment(strategyId, amount);
      const receipt = await tx.wait();
      const event = receipt.events.find((e) => e.event === "InvestmentCreated");
      const investmentId = event.args.investmentId;

      expect(await assetToken.balanceOf(feeCollector.address)).to.equal(fee);

      const investment = await defi.investments(investmentId);
      expect(investment.amount).to.equal(amount.sub(fee));
      expect(investment.initialValue).to.equal(amount.sub(fee));
      expect(investment.currentValue).to.equal(amount.sub(fee));
      expect(investment.isActive).to.equal(true);
    });

    it("rejects investments below the strategy minimum", async function () {
      const strategyId = await createStrategy({
        minInvestment: ethers.utils.parseEther("500"),
      });
      await expect(
        defi
          .connect(alice)
          .createInvestment(strategyId, ethers.utils.parseEther("100")),
      ).to.be.revertedWith("Amount below minimum");
    });

    it("rejects investments above the strategy maximum", async function () {
      const strategyId = await createStrategy({
        maxInvestment: ethers.utils.parseEther("500"),
      });
      await expect(
        defi
          .connect(alice)
          .createInvestment(strategyId, ethers.utils.parseEther("1000")),
      ).to.be.revertedWith("Amount above maximum");
    });

    it("rejects investments while investments are disabled", async function () {
      const strategyId = await createStrategy();
      await defi.setInvestmentsEnabled(false);
      await expect(
        defi
          .connect(alice)
          .createInvestment(strategyId, ethers.utils.parseEther("1000")),
      ).to.be.revertedWith("Investments not enabled");
    });
  });

  describe("closeInvestment (investor self-service)", function () {
    it("reverts before the lock period ends", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      await expect(
        defi.connect(alice).closeInvestment(investmentId),
      ).to.be.revertedWith("Lock period not ended");
    });

    it("pays out exactly the oracle-attested currentValue after the lock period", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      // Owner attests a new valuation (simulating accrued yield); fund the
      // contract so it can actually pay it out.
      const investment = await defi.investments(investmentId);
      const payout = investment.currentValue.add(ethers.utils.parseEther("50"));
      await assetToken.transfer(defi.address, ethers.utils.parseEther("50"));
      await defi.updateInvestmentValue(investmentId, payout);

      await time.increase(LOCK_PERIOD + 1);

      const balanceBefore = await assetToken.balanceOf(alice.address);
      await defi.connect(alice).closeInvestment(investmentId);
      const balanceAfter = await assetToken.balanceOf(alice.address);

      expect(balanceAfter.sub(balanceBefore)).to.equal(payout);
    });

    it("cannot be called by anyone other than the investor", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      await time.increase(LOCK_PERIOD + 1);

      await expect(
        defi.connect(owner).closeInvestment(investmentId),
      ).to.be.revertedWith("Not investor");
    });

    it("does NOT let the investor dictate an arbitrary final value", async function () {
      // Regression test for a critical bug: previously closeInvestment took
      // a caller-supplied _finalValue, letting any investor drain the
      // contract's pooled balance. The fixed function takes no such
      // parameter and only ever pays out investment.currentValue.
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      // Fund the contract generously so a payout would succeed if the bug
      // still existed.
      await assetToken.transfer(defi.address, ethers.utils.parseEther("50000"));

      await time.increase(LOCK_PERIOD + 1);

      const investment = await defi.investments(investmentId);
      const balanceBefore = await assetToken.balanceOf(alice.address);

      await defi.connect(alice).closeInvestment(investmentId);

      const balanceAfter = await assetToken.balanceOf(alice.address);
      expect(balanceAfter.sub(balanceBefore)).to.equal(investment.currentValue);
    });
  });

  describe("forceCloseInvestment (owner override)", function () {
    it("lets the owner close with a custom value, bypassing the lock period", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      const customValue = ethers.utils.parseEther("1200");
      await assetToken.transfer(defi.address, ethers.utils.parseEther("1000"));

      const balanceBefore = await assetToken.balanceOf(alice.address);
      await expect(defi.forceCloseInvestment(investmentId, customValue))
        .to.emit(defi, "InvestmentForceClosed")
        .withArgs(investmentId, customValue);
      const balanceAfter = await assetToken.balanceOf(alice.address);

      expect(balanceAfter.sub(balanceBefore)).to.equal(customValue);
    });

    it("is restricted to the owner", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      await expect(
        defi
          .connect(alice)
          .forceCloseInvestment(investmentId, ethers.utils.parseEther("1")),
      ).to.be.revertedWithCustomError(defi, "OwnableUnauthorizedAccount");
    });
  });

  describe("claimYield", function () {
    it("reverts with 'Insufficient yield' when no yield has accrued yet", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      await expect(
        defi.connect(alice).claimYield(investmentId, 1),
      ).to.be.revertedWith("Insufficient yield");
    });

    it("reverts with 'No yield available' if the valuation has dropped below the initial value", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      const investment = await defi.investments(investmentId);
      await defi.updateInvestmentValue(
        investmentId,
        investment.currentValue.sub(ethers.utils.parseEther("10")),
      );

      await expect(
        defi.connect(alice).claimYield(investmentId, 1),
      ).to.be.revertedWith("No yield available");
    });

    it("lets the investor claim accrued yield up to the available amount", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      const investment = await defi.investments(investmentId);
      const yieldAmount = ethers.utils.parseEther("20");
      await assetToken.transfer(defi.address, yieldAmount);
      await defi.updateInvestmentValue(
        investmentId,
        investment.currentValue.add(yieldAmount),
      );

      const balanceBefore = await assetToken.balanceOf(alice.address);
      await defi.connect(alice).claimYield(investmentId, yieldAmount);
      const balanceAfter = await assetToken.balanceOf(alice.address);

      expect(balanceAfter.sub(balanceBefore)).to.equal(yieldAmount);
    });

    it("rejects a zero-amount claim", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      await expect(
        defi.connect(alice).claimYield(investmentId, 0),
      ).to.be.revertedWith("Amount must be greater than 0");
    });
  });

  describe("Admin settings and user views", function () {
    it("rejects a platform fee above 1%", async function () {
      await expect(defi.setPlatformFee(101)).to.be.revertedWith("Fee too high");
    });

    it("lets the owner update the platform fee", async function () {
      await expect(defi.setPlatformFee(50))
        .to.emit(defi, "PlatformFeeUpdated")
        .withArgs(50);
      expect(await defi.platformFee()).to.equal(50);
    });

    it("rejects a zero fee collector", async function () {
      await expect(
        defi.setFeeCollector(ethers.constants.AddressZero),
      ).to.be.revertedWith("Invalid fee collector");
    });

    it("lets the owner update the fee collector", async function () {
      await expect(defi.setFeeCollector(alice.address))
        .to.emit(defi, "FeeCollectorUpdated")
        .withArgs(alice.address);
      expect(await defi.feeCollector()).to.equal(alice.address);
    });

    it("lists a user's investments and yield claims", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      const investment = await defi.investments(investmentId);
      const yieldAmount = ethers.utils.parseEther("10");
      await assetToken.transfer(defi.address, yieldAmount);
      await defi.updateInvestmentValue(
        investmentId,
        investment.currentValue.add(yieldAmount),
      );
      await defi.connect(alice).claimYield(investmentId, yieldAmount);

      const userInvestments = await defi.getUserInvestments(alice.address);
      expect(userInvestments.map((id) => id.toString())).to.include(
        investmentId.toString(),
      );

      const userClaims = await defi.getUserYieldClaims(alice.address);
      expect(userClaims.length).to.equal(1);
    });

    it("returns only active investments for a user", async function () {
      const strategyId = await createStrategy();
      const tx = await defi
        .connect(alice)
        .createInvestment(strategyId, ethers.utils.parseEther("1000"));
      const receipt = await tx.wait();
      const investmentId = receipt.events.find(
        (e) => e.event === "InvestmentCreated",
      ).args.investmentId;

      await time.increase(LOCK_PERIOD + 1);
      await defi.connect(alice).closeInvestment(investmentId);

      const active = await defi.getActiveInvestmentsForUser(alice.address);
      expect(active.length).to.equal(0);
    });
  });
});
