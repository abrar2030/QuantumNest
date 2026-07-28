import { formatCurrency, formatPercentage, getInitials, shortenAddress } from "../utils";

describe("Utils", () => {
  describe("formatCurrency", () => {
    it("formats positive numbers correctly", () => {
      expect(formatCurrency(1000)).toBe("$1,000.00");
      expect(formatCurrency(1500.5)).toBe("$1,500.50");
    });

    it("formats large numbers correctly", () => {
      expect(formatCurrency(1000000)).toBe("$1,000,000.00");
    });

    it("formats zero correctly", () => {
      expect(formatCurrency(0)).toBe("$0.00");
    });
  });

  describe("formatPercentage", () => {
    it("formats positive percentages correctly", () => {
      expect(formatPercentage(5.5)).toBe("5.50%");
      expect(formatPercentage(10)).toBe("10.00%");
    });

    it("formats negative percentages correctly", () => {
      expect(formatPercentage(-3.2)).toBe("-3.20%");
    });

    it("formats zero correctly", () => {
      expect(formatPercentage(0)).toBe("0.00%");
    });
  });

  describe("shortenAddress", () => {
    it("keeps the leading and trailing characters and elides the middle", () => {
      const address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e";
      const result = shortenAddress(address);
      expect(result.startsWith("0x742d")).toBe(true);
      expect(result.endsWith("f44e")).toBe(true);
      expect(result).toContain("...");
    });
  });

  describe("getInitials", () => {
    it("builds initials from a full name", () => {
      expect(getInitials("Ada Lovelace")).toBe("AL");
    });

    it("falls back gracefully when no name is given", () => {
      expect(getInitials(null)).toBe("QN");
    });
  });
});
