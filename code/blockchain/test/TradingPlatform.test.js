const { expect } = require("chai");
const { ethers } = require("hardhat");

const TRADE_FEE_BPS = 25; // 0.25%

describe("TradingPlatform", function () {
  let tradingPlatform, assetToken, paymentToken;
  let owner, feeCollector, alice, bob;

  beforeEach(async function () {
    [owner, feeCollector, alice, bob] = await ethers.getSigners();

    const TestToken = await ethers.getContractFactory("TestToken");
    // Asset being traded (e.g. a tokenized stock)
    assetToken = await TestToken.deploy();
    await assetToken.deployed();
    // Stablecoin used to pay for trades
    paymentToken = await TestToken.deploy();
    await paymentToken.deployed();

    const TradingPlatform = await ethers.getContractFactory("TradingPlatform");
    tradingPlatform = await TradingPlatform.deploy(
      TRADE_FEE_BPS,
      feeCollector.address,
      paymentToken.address,
    );
    await tradingPlatform.deployed();

    await tradingPlatform.whitelistToken(assetToken.address);
    await tradingPlatform.setTradingEnabled(true);

    // Fund alice (seller) with asset tokens, bob (buyer) with payment tokens
    await assetToken.transfer(alice.address, ethers.utils.parseEther("1000"));
    await paymentToken.transfer(
      bob.address,
      ethers.utils.parseEther("1000000"),
    );

    // Approvals
    await assetToken
      .connect(alice)
      .approve(tradingPlatform.address, ethers.constants.MaxUint256);
    await paymentToken
      .connect(bob)
      .approve(tradingPlatform.address, ethers.constants.MaxUint256);
  });

  describe("Constructor validation", function () {
    it("rejects a trading fee above 1%", async function () {
      const TradingPlatform =
        await ethers.getContractFactory("TradingPlatform");
      await expect(
        TradingPlatform.deploy(101, feeCollector.address, paymentToken.address),
      ).to.be.revertedWith("Fee too high");
    });

    it("rejects a zero fee collector", async function () {
      const TradingPlatform =
        await ethers.getContractFactory("TradingPlatform");
      await expect(
        TradingPlatform.deploy(
          TRADE_FEE_BPS,
          ethers.constants.AddressZero,
          paymentToken.address,
        ),
      ).to.be.revertedWith("Invalid fee collector");
    });

    it("rejects a zero payment token", async function () {
      const TradingPlatform =
        await ethers.getContractFactory("TradingPlatform");
      await expect(
        TradingPlatform.deploy(
          TRADE_FEE_BPS,
          feeCollector.address,
          ethers.constants.AddressZero,
        ),
      ).to.be.revertedWith("Invalid payment token");
    });
  });

  describe("Order creation guards", function () {
    it("rejects orders when trading is disabled", async function () {
      await tradingPlatform.setTradingEnabled(false);
      await expect(
        tradingPlatform
          .connect(alice)
          .createOrder(assetToken.address, 10, 100, false),
      ).to.be.revertedWith("Trading not enabled");
    });

    it("rejects orders for non-whitelisted tokens", async function () {
      const otherToken = await (
        await ethers.getContractFactory("TestToken")
      ).deploy();
      await expect(
        tradingPlatform
          .connect(alice)
          .createOrder(otherToken.address, 10, 100, false),
      ).to.be.revertedWith("Token not whitelisted");
    });

    it("rejects a sell order without sufficient asset allowance", async function () {
      await assetToken.connect(alice).approve(tradingPlatform.address, 0);
      await expect(
        tradingPlatform
          .connect(alice)
          .createOrder(
            assetToken.address,
            ethers.utils.parseEther("10"),
            100,
            false,
          ),
      ).to.be.revertedWith("Insufficient token allowance");
    });

    it("rejects a buy order without sufficient payment token allowance", async function () {
      await paymentToken.connect(bob).approve(tradingPlatform.address, 0);
      await expect(
        tradingPlatform
          .connect(bob)
          .createOrder(
            assetToken.address,
            ethers.utils.parseEther("10"),
            100,
            true,
          ),
      ).to.be.revertedWith("Insufficient payment token allowance");
    });

    it("rejects a buy order without sufficient payment token balance", async function () {
      const poorBuyer = (await ethers.getSigners())[5];
      await paymentToken
        .connect(poorBuyer)
        .approve(tradingPlatform.address, ethers.constants.MaxUint256);
      await expect(
        tradingPlatform
          .connect(poorBuyer)
          .createOrder(
            assetToken.address,
            ethers.utils.parseEther("10"),
            100,
            true,
          ),
      ).to.be.revertedWith("Insufficient payment token balance");
    });
  });

  describe("Matching and settlement", function () {
    it("settles a matched trade: buyer pays, seller receives tokens and net payment", async function () {
      const amount = ethers.utils.parseEther("10");
      const price = 200; // arbitrary price unit, e.g. USD cents per whole token
      const rawTotalValue = amount.mul(price);
      const fee = rawTotalValue.mul(TRADE_FEE_BPS).div(10000);

      const sellerAssetBefore = await assetToken.balanceOf(alice.address);
      const buyerPaymentBefore = await paymentToken.balanceOf(bob.address);

      // Seller lists first
      await tradingPlatform
        .connect(alice)
        .createOrder(assetToken.address, amount, price, false);

      // Buyer's matching order triggers execution
      await expect(
        tradingPlatform
          .connect(bob)
          .createOrder(assetToken.address, amount, price, true),
      ).to.emit(tradingPlatform, "TradeExecuted");

      // Buyer received the asset tokens
      expect(await assetToken.balanceOf(bob.address)).to.equal(amount);
      // Seller's asset balance decreased
      expect(await assetToken.balanceOf(alice.address)).to.equal(
        sellerAssetBefore.sub(amount),
      );

      // Seller received payment net of fee
      expect(await paymentToken.balanceOf(alice.address)).to.equal(
        rawTotalValue.sub(fee),
      );
      // Buyer paid the full amount (net + fee)
      expect(await paymentToken.balanceOf(bob.address)).to.equal(
        buyerPaymentBefore.sub(rawTotalValue),
      );
      // Fee collector received the fee
      expect(await paymentToken.balanceOf(feeCollector.address)).to.equal(fee);

      // Both orders should be fully filled
      const buyOrder = await tradingPlatform.orders(2);
      const sellOrder = await tradingPlatform.orders(1);
      expect(buyOrder.isActive).to.equal(false);
      expect(sellOrder.isActive).to.equal(false);
    });

    it("does not move any payment tokens when no match occurs", async function () {
      await tradingPlatform
        .connect(alice)
        .createOrder(
          assetToken.address,
          ethers.utils.parseEther("10"),
          100,
          false,
        );

      expect(await paymentToken.balanceOf(alice.address)).to.equal(0);
      expect(await assetToken.balanceOf(alice.address)).to.equal(
        ethers.utils.parseEther("1000"),
      );
    });

    it("partially fills the larger order and keeps it active", async function () {
      const sellAmount = ethers.utils.parseEther("10");
      const buyAmount = ethers.utils.parseEther("4");
      const price = 100;

      await tradingPlatform
        .connect(alice)
        .createOrder(assetToken.address, sellAmount, price, false);
      await tradingPlatform
        .connect(bob)
        .createOrder(assetToken.address, buyAmount, price, true);

      const sellOrder = await tradingPlatform.orders(1);
      expect(sellOrder.isActive).to.equal(true);
      expect(sellOrder.amount).to.equal(sellAmount.sub(buyAmount));

      const buyOrder = await tradingPlatform.orders(2);
      expect(buyOrder.isActive).to.equal(false);
    });
  });

  describe("cancelOrder", function () {
    it("allows the maker to cancel their own order", async function () {
      await tradingPlatform
        .connect(alice)
        .createOrder(
          assetToken.address,
          ethers.utils.parseEther("10"),
          100,
          false,
        );

      await expect(tradingPlatform.connect(alice).cancelOrder(1))
        .to.emit(tradingPlatform, "OrderCancelled")
        .withArgs(1);

      const order = await tradingPlatform.orders(1);
      expect(order.isActive).to.equal(false);
    });

    it("reverts if a non-maker tries to cancel", async function () {
      await tradingPlatform
        .connect(alice)
        .createOrder(
          assetToken.address,
          ethers.utils.parseEther("10"),
          100,
          false,
        );

      await expect(
        tradingPlatform.connect(bob).cancelOrder(1),
      ).to.be.revertedWith("Not order maker");
    });
  });

  describe("Admin functions", function () {
    it("rejects a trading fee update above 1%", async function () {
      await expect(tradingPlatform.setTradingFee(200)).to.be.revertedWith(
        "Fee too high",
      );
    });

    it("emits TokenWhitelisted / TokenRemovedFromWhitelist", async function () {
      const otherToken = await (
        await ethers.getContractFactory("TestToken")
      ).deploy();
      await expect(tradingPlatform.whitelistToken(otherToken.address)).to.emit(
        tradingPlatform,
        "TokenWhitelisted",
      );
      await expect(
        tradingPlatform.removeTokenFromWhitelist(otherToken.address),
      ).to.emit(tradingPlatform, "TokenRemovedFromWhitelist");
    });

    it("restricts admin functions to the owner", async function () {
      await expect(
        tradingPlatform.connect(alice).setTradingEnabled(false),
      ).to.be.revertedWithCustomError(
        tradingPlatform,
        "OwnableUnauthorizedAccount",
      );
    });

    it("lets the owner update the fee collector", async function () {
      await expect(tradingPlatform.setFeeCollector(alice.address))
        .to.emit(tradingPlatform, "FeeCollectorUpdated")
        .withArgs(alice.address);
      expect(await tradingPlatform.feeCollector()).to.equal(alice.address);
    });

    it("rejects a zero fee collector", async function () {
      await expect(
        tradingPlatform.setFeeCollector(ethers.constants.AddressZero),
      ).to.be.revertedWith("Invalid fee collector");
    });

    it("lets the owner update the payment token", async function () {
      const newPaymentToken = await (
        await ethers.getContractFactory("TestToken")
      ).deploy();
      await expect(tradingPlatform.setPaymentToken(newPaymentToken.address))
        .to.emit(tradingPlatform, "PaymentTokenUpdated")
        .withArgs(newPaymentToken.address);
      expect(await tradingPlatform.paymentToken()).to.equal(
        newPaymentToken.address,
      );
    });

    it("rejects a zero payment token on update", async function () {
      await expect(
        tradingPlatform.setPaymentToken(ethers.constants.AddressZero),
      ).to.be.revertedWith("Invalid payment token");
    });
  });

  describe("User-scoped views", function () {
    it("lists a user's buy orders, sell orders and trades", async function () {
      const amount = ethers.utils.parseEther("10");
      const price = 200;

      await tradingPlatform
        .connect(alice)
        .createOrder(assetToken.address, amount, price, false);
      await tradingPlatform
        .connect(bob)
        .createOrder(assetToken.address, amount, price, true);

      const aliceSellOrders = await tradingPlatform.getUserSellOrders(
        alice.address,
      );
      expect(aliceSellOrders.map((id) => id.toString())).to.deep.equal(["1"]);

      const bobBuyOrders = await tradingPlatform.getUserBuyOrders(bob.address);
      expect(bobBuyOrders.map((id) => id.toString())).to.deep.equal(["2"]);

      const aliceTrades = await tradingPlatform.getUserTrades(alice.address);
      const bobTrades = await tradingPlatform.getUserTrades(bob.address);
      expect(aliceTrades.length).to.equal(1);
      expect(bobTrades.length).to.equal(1);
    });

    it("returns active orders for a token filtered by side", async function () {
      const amount = ethers.utils.parseEther("10");

      await tradingPlatform
        .connect(alice)
        .createOrder(assetToken.address, amount, 150, false);
      await tradingPlatform
        .connect(alice)
        .createOrder(assetToken.address, amount, 250, false);

      const sellOrders = await tradingPlatform.getActiveOrders(
        assetToken.address,
        false,
        0,
        10,
      );
      expect(sellOrders.length).to.equal(2);

      const buyOrders = await tradingPlatform.getActiveOrders(
        assetToken.address,
        true,
        0,
        10,
      );
      expect(buyOrders.length).to.equal(0);
    });
  });
});
