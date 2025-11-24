// tests/digest-bot.test.js

import { describe, it, expect, vi, beforeEach } from "vitest";

// We'll test the pure functions that don't require network access
const {
  calculateEmojiStats,
  generateDigestMarkdown,
} = require("../bot/digest-bot.js");

describe("digest-bot", () => {
  describe("calculateEmojiStats", () => {
    it("should calculate correct emoji counts and percentages", () => {
      const reactions = [
        { content: "+1", user: "agent-1", issue: "Issue A" },
        { content: "+1", user: "agent-2", issue: "Issue A" },
        { content: "+1", user: "agent-1", issue: "Issue B" },
        { content: "-1", user: "agent-3", issue: "Issue C" },
        { content: "confused", user: "agent-3", issue: "Issue D" },
        { content: "eyes", user: "agent-1", issue: "Issue E" },
      ];

      const stats = calculateEmojiStats(reactions);

      expect(stats.total).toBe(6);
      expect(stats.stats.length).toBe(4);

      // +1 should be most common with 50%
      const plusOne = stats.stats.find((s) => s.rawEmoji === "+1");
      expect(plusOne.count).toBe(3);
      expect(plusOne.percentage).toBe(50);
      expect(plusOne.emoji).toBe("✅");

      // -1 should have 1 count
      const minusOne = stats.stats.find((s) => s.rawEmoji === "-1");
      expect(minusOne.count).toBe(1);
      expect(minusOne.emoji).toBe("❌");
    });

    it("should identify most active agent", () => {
      const reactions = [
        { content: "+1", user: "scribe-agent", issue: "Issue A" },
        { content: "+1", user: "scribe-agent", issue: "Issue B" },
        { content: "+1", user: "scribe-agent", issue: "Issue C" },
        { content: "-1", user: "builder-agent", issue: "Issue D" },
      ];

      const stats = calculateEmojiStats(reactions);

      expect(stats.mostActiveAgent).toBe("scribe-agent");
    });

    it("should identify most blocked issue", () => {
      const reactions = [
        { content: "-1", user: "agent-1", issue: "blackroad-os-api" },
        { content: "-1", user: "agent-2", issue: "blackroad-os-api" },
        { content: "confused", user: "agent-3", issue: "blackroad-os-api" },
        { content: "-1", user: "agent-4", issue: "other-issue" },
      ];

      const stats = calculateEmojiStats(reactions);

      expect(stats.mostBlocked).toBe("blackroad-os-api");
      expect(stats.blockedCount).toBe(4);
    });

    it("should handle empty reactions array", () => {
      const stats = calculateEmojiStats([]);

      expect(stats.total).toBe(0);
      expect(stats.stats.length).toBe(0);
      expect(stats.mostActiveAgent).toBeNull();
      expect(stats.mostBlocked).toBeNull();
    });

    it("should count escalations and review requests", () => {
      const reactions = [
        { content: "rotating_light", user: "agent-1", issue: "Issue A" },
        { content: "rotating_light", user: "agent-2", issue: "Issue B" },
        { content: "thinking_face", user: "agent-3", issue: "Issue C" },
      ];

      const stats = calculateEmojiStats(reactions);

      expect(stats.escalationCount).toBe(2);
      expect(stats.reviewCount).toBe(1);
    });
  });

  describe("generateDigestMarkdown", () => {
    it("should generate valid markdown table", () => {
      const stats = {
        total: 10,
        stats: [
          { emoji: "✅", rawEmoji: "+1", count: 5, percentage: 50 },
          { emoji: "❌", rawEmoji: "-1", count: 3, percentage: 30 },
          { emoji: "🛟", rawEmoji: "rotating_light", count: 2, percentage: 20 },
        ],
        mostActiveAgent: "@scribe-agent",
        mostBlocked: "blackroad-os-api",
        blockedCount: 3,
        escalationCount: 2,
        reviewCount: 1,
      };

      const testDate = new Date("2025-11-24");
      const markdown = generateDigestMarkdown(stats, testDate);

      expect(markdown).toContain("# 📊 Weekly Agent Emoji Digest");
      expect(markdown).toContain("Nov 24, 2025");
      expect(markdown).toContain("| Emoji | Count | % |");
      expect(markdown).toContain("| ✅ | 5 | 50% |");
      expect(markdown).toContain("| ❌ | 3 | 30% |");
      expect(markdown).toContain("| 🛟 | 2 | 20% |");
      expect(markdown).toContain("🔥 Most active agent: `@scribe-agent`");
      expect(markdown).toContain("🛑 Most blocked: `blackroad-os-api`");
      expect(markdown).toContain("🛟 Escalations: 2 cases");
      expect(markdown).toContain("🤔 Review queue: 1 issues");
    });

    it("should handle empty stats gracefully", () => {
      const stats = {
        total: 0,
        stats: [],
        mostActiveAgent: null,
        mostBlocked: null,
        blockedCount: 0,
        escalationCount: 0,
        reviewCount: 0,
      };

      const testDate = new Date("2025-11-24");
      const markdown = generateDigestMarkdown(stats, testDate);

      expect(markdown).toContain("# 📊 Weekly Agent Emoji Digest");
      expect(markdown).toContain("| Emoji | Count | % |");
      // Should not contain agent/blocked info when null
      expect(markdown).not.toContain("Most active agent");
      expect(markdown).not.toContain("Most blocked");
    });
  });
});
