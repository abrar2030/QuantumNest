const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TestToken", function () {
  let testToken;
  let owner, addr1, addr2;

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();
    const TestToken = await ethers.getContractFactory("TestToken");
    testToken = await TestToken.deploy();
    await testToken.deployed();
  });

  describe("Deployment", function () {
    it("sets the right name and symbol", async function () {
      expect(await testToken.name()).to.equal("QuantumNest Test Token");
      expect(await testToken.symbol()).to.equal("QNT");
    });

    it("mints the initial supply to the deployer", async function () {
      const expected = ethers.utils.parseEther("1000000");
      expect(await testToken.totalSupply()).to.equal(expected);
      expect(await testToken.balanceOf(owner.address)).to.equal(expected);
    });

    it("sets the deployer as owner", async function () {
      expect(await testToken.owner()).to.equal(owner.address);
    });
  });

  describe("mint", function () {
    it("allows the owner to mint new tokens", async function () {
      const amount = ethers.utils.parseEther("100");
      await expect(testToken.mint(addr1.address, amount))
        .to.emit(testToken, "Transfer")
        .withArgs(ethers.constants.AddressZero, addr1.address, amount);

      expect(await testToken.balanceOf(addr1.address)).to.equal(amount);
    });

    it("reverts when a non-owner tries to mint", async function () {
      const amount = ethers.utils.parseEther("100");
      await expect(
        testToken.connect(addr1).mint(addr1.address, amount),
      ).to.be.revertedWithCustomError(testToken, "OwnableUnauthorizedAccount");
    });
  });

  describe("burn", function () {
    it("allows a token holder to burn their own tokens", async function () {
      const amount = ethers.utils.parseEther("50");
      await testToken.transfer(addr1.address, amount);

      await expect(testToken.connect(addr1).burn(amount))
        .to.emit(testToken, "Transfer")
        .withArgs(addr1.address, ethers.constants.AddressZero, amount);

      expect(await testToken.balanceOf(addr1.address)).to.equal(0);
    });

    it("reverts if burning more than the balance", async function () {
      const amount = ethers.utils.parseEther("1");
      await expect(
        testToken.connect(addr2).burn(amount),
      ).to.be.revertedWithCustomError(testToken, "ERC20InsufficientBalance");
    });
  });
});
