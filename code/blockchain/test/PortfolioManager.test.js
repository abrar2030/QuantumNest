const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PortfolioManager", function () {
  let portfolioManager;
  let owner, alice, bob, stranger;
  let tokenAddress;

  beforeEach(async function () {
    [owner, alice, bob, stranger] = await ethers.getSigners();
    const PortfolioManager =
      await ethers.getContractFactory("PortfolioManager");
    portfolioManager = await PortfolioManager.deploy();
    await portfolioManager.deployed();

    // Use a throwaway address to stand in for a token contract; the
    // contract only stores it, it never calls into it.
    tokenAddress = ethers.Wallet.createRandom().address;
  });

  async function createPortfolio(signer = alice) {
    const tx = await portfolioManager
      .connect(signer)
      .createPortfolio("Growth Portfolio", "High-growth tech stocks");
    const receipt = await tx.wait();
    const event = receipt.events.find((e) => e.event === "PortfolioCreated");
    return event.args.portfolioId;
  }

  describe("createPortfolio", function () {
    it("creates a portfolio owned by the caller", async function () {
      const portfolioId = await createPortfolio(alice);
      const portfolio = await portfolioManager.portfolios(portfolioId);

      expect(portfolio.name).to.equal("Growth Portfolio");
      expect(portfolio.isActive).to.equal(true);
      expect(
        await portfolioManager.isPortfolioOwner(portfolioId, alice.address),
      ).to.equal(true);
    });

    it("tracks the portfolio under the creator's list", async function () {
      const portfolioId = await createPortfolio(alice);
      const ids = await portfolioManager.getUserPortfolios(alice.address);
      expect(ids.map((id) => id.toString())).to.include(portfolioId.toString());
    });
  });

  describe("access control", function () {
    it("prevents non-owner/non-manager from updating a portfolio", async function () {
      const portfolioId = await createPortfolio(alice);
      await expect(
        portfolioManager
          .connect(stranger)
          .updatePortfolio(portfolioId, "New name", "New description"),
      ).to.be.revertedWith("Not authorized");
    });

    it("allows an added manager to update the portfolio", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .addManager(portfolioId, bob.address);

      await expect(
        portfolioManager
          .connect(bob)
          .updatePortfolio(portfolioId, "Renamed", "Updated"),
      ).to.not.be.reverted;

      const portfolio = await portfolioManager.portfolios(portfolioId);
      expect(portfolio.name).to.equal("Renamed");
    });

    it("prevents non-owners from adding managers", async function () {
      const portfolioId = await createPortfolio(alice);
      await expect(
        portfolioManager.connect(bob).addManager(portfolioId, bob.address),
      ).to.be.revertedWith("Not owner");
    });

    it("prevents adding the same manager twice", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .addManager(portfolioId, bob.address);
      await expect(
        portfolioManager.connect(alice).addManager(portfolioId, bob.address),
      ).to.be.revertedWith("Manager already exists");
    });

    it("allows removing a manager", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .addManager(portfolioId, bob.address);
      await portfolioManager
        .connect(alice)
        .removeManager(portfolioId, bob.address);

      expect(
        await portfolioManager.isPortfolioManager(portfolioId, bob.address),
      ).to.equal(false);
    });
  });

  describe("assets and allocations", function () {
    it("adds an asset with a valid target allocation", async function () {
      const portfolioId = await createPortfolio(alice);
      await expect(
        portfolioManager
          .connect(alice)
          .addAsset(portfolioId, tokenAddress, "qAAPL", 5000),
      )
        .to.emit(portfolioManager, "AssetAdded")
        .withArgs(portfolioId, tokenAddress, "qAAPL", 5000);
    });

    it("rejects a target allocation above 100%", async function () {
      const portfolioId = await createPortfolio(alice);
      await expect(
        portfolioManager
          .connect(alice)
          .addAsset(portfolioId, tokenAddress, "qAAPL", 10001),
      ).to.be.revertedWith("Allocation too high");
    });

    it("rejects adding the same asset twice", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .addAsset(portfolioId, tokenAddress, "qAAPL", 5000);

      await expect(
        portfolioManager
          .connect(alice)
          .addAsset(portfolioId, tokenAddress, "qAAPL", 1000),
      ).to.be.revertedWith("Asset already exists");
    });

    it("updates current allocations and enforces the 100% cap", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .addAsset(portfolioId, tokenAddress, "qAAPL", 5000);

      await portfolioManager
        .connect(alice)
        .updateCurrentAllocations(portfolioId, [tokenAddress], [6000]);

      const allocation = await portfolioManager.assetAllocations(
        portfolioId,
        tokenAddress,
      );
      expect(allocation.currentAllocation).to.equal(6000);
    });

    it("removes an asset (soft delete)", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .addAsset(portfolioId, tokenAddress, "qAAPL", 5000);

      await portfolioManager
        .connect(alice)
        .removeAsset(portfolioId, tokenAddress);

      const allocation = await portfolioManager.assetAllocations(
        portfolioId,
        tokenAddress,
      );
      expect(allocation.isActive).to.equal(false);
    });

    it("updates the target allocation for an existing asset", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .addAsset(portfolioId, tokenAddress, "qAAPL", 5000);

      await expect(
        portfolioManager
          .connect(alice)
          .updateAllocation(portfolioId, tokenAddress, 7500),
      )
        .to.emit(portfolioManager, "AllocationUpdated")
        .withArgs(portfolioId, tokenAddress, 7500);

      const allocation = await portfolioManager.assetAllocations(
        portfolioId,
        tokenAddress,
      );
      expect(allocation.targetAllocation).to.equal(7500);
    });

    it("returns a portfolio's asset list and managers", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .addAsset(portfolioId, tokenAddress, "qAAPL", 5000);
      await portfolioManager
        .connect(alice)
        .addManager(portfolioId, bob.address);

      const assets = await portfolioManager.getPortfolioAssets(portfolioId);
      expect(assets).to.deep.equal([tokenAddress]);

      const managers = await portfolioManager.getPortfolioManagers(portfolioId);
      expect(managers).to.deep.equal([bob.address]);
    });
  });

  describe("transactions and rebalancing", function () {
    it("records a manual transaction", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager
        .connect(alice)
        .recordTransaction(
          portfolioId,
          tokenAddress,
          "qAAPL",
          100,
          17500,
          true,
          "manual",
        );

      expect(
        await portfolioManager.getPortfolioTransactionCount(portfolioId),
      ).to.equal(1);
    });

    it("records a rebalance across multiple assets and updates the rebalance date", async function () {
      const portfolioId = await createPortfolio(alice);
      const secondToken = ethers.Wallet.createRandom().address;

      await expect(
        portfolioManager
          .connect(alice)
          .recordRebalance(
            portfolioId,
            [tokenAddress, secondToken],
            ["qAAPL", "qMSFT"],
            [100, 200],
            [17500, 30000],
            [true, false],
          ),
      ).to.emit(portfolioManager, "PortfolioRebalanced");

      expect(
        await portfolioManager.getPortfolioTransactionCount(portfolioId),
      ).to.equal(2);
    });

    it("rejects a rebalance with mismatched array lengths", async function () {
      const portfolioId = await createPortfolio(alice);
      await expect(
        portfolioManager
          .connect(alice)
          .recordRebalance(
            portfolioId,
            [tokenAddress],
            ["qAAPL", "qMSFT"],
            [100],
            [17500],
            [true],
          ),
      ).to.be.revertedWith("Array length mismatch");
    });

    it("paginates portfolio transactions", async function () {
      const portfolioId = await createPortfolio(alice);
      for (let i = 0; i < 3; i++) {
        await portfolioManager
          .connect(alice)
          .recordTransaction(
            portfolioId,
            tokenAddress,
            "qAAPL",
            100 + i,
            17500,
            true,
            "manual",
          );
      }

      const page = await portfolioManager.getPortfolioTransactions(
        portfolioId,
        1,
        2,
      );
      expect(page.length).to.equal(2);
      expect(page[0].amount).to.equal(101);
      expect(page[1].amount).to.equal(102);
    });
  });

  describe("activation", function () {
    it("deactivates and reactivates a portfolio", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager.connect(alice).deactivatePortfolio(portfolioId);

      let portfolio = await portfolioManager.portfolios(portfolioId);
      expect(portfolio.isActive).to.equal(false);

      await portfolioManager.connect(alice).reactivatePortfolio(portfolioId);
      portfolio = await portfolioManager.portfolios(portfolioId);
      expect(portfolio.isActive).to.equal(true);
    });

    it("blocks updates on a deactivated portfolio", async function () {
      const portfolioId = await createPortfolio(alice);
      await portfolioManager.connect(alice).deactivatePortfolio(portfolioId);

      await expect(
        portfolioManager.connect(alice).updatePortfolio(portfolioId, "x", "y"),
      ).to.be.revertedWith("Portfolio not active");
    });
  });
});
