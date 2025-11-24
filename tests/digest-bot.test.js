// tests/digest-bot.test.js
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("digest-bot", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv, GITHUB_TOKEN: "test-token" };
    mockFetch.mockReset();
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe("calculateReactionStats", () => {
    it("should calculate statistics from issues with reactions", async () => {
      const { calculateReactionStats } = await import("../bot/handlers/digest-bot.js");

      const mockIssues = [
        {
          number: 1,
          title: "Test Issue 1",
          reactions: {
            nodes: [
              { content: "THUMBS_UP", user: { login: "agent-1" } },
              { content: "THUMBS_UP", user: { login: "agent-2" } },
              { content: "HEART", user: { login: "agent-1" } },
            ],
          },
          comments: { nodes: [] },
          labels: { nodes: [{ name: "bug" }] },
        },
        {
          number: 2,
          title: "Test Issue 2",
          reactions: {
            nodes: [
              { content: "THUMBS_DOWN", user: { login: "agent-1" } },
            ],
          },
          comments: { nodes: [] },
          labels: { nodes: [{ name: "bug" }] },
        },
      ];

      const stats = calculateReactionStats(mockIssues);

      expect(stats.total).toBe(4);
      expect(stats.byEmoji["👍"]).toBe(2);
      expect(stats.byEmoji["❤️"]).toBe(1);
      expect(stats.byEmoji["👎"]).toBe(1);
      expect(stats.mostActiveAgent).toBe("agent-1");
      expect(stats.blockedIssues).toContain(2);
    });

    it("should handle empty issues array", async () => {
      const { calculateReactionStats } = await import("../bot/handlers/digest-bot.js");

      const stats = calculateReactionStats([]);

      expect(stats.total).toBe(0);
      expect(stats.byEmoji).toEqual({});
    });

    it("should count comment reactions", async () => {
      const { calculateReactionStats } = await import("../bot/handlers/digest-bot.js");

      const mockIssues = [
        {
          number: 1,
          title: "Test Issue",
          reactions: { nodes: [] },
          comments: {
            nodes: [
              {
                author: { login: "commenter" },
                reactions: {
                  nodes: [
                    { content: "ROCKET", user: { login: "agent-1" } },
                    { content: "EYES", user: { login: "agent-2" } },
                  ],
                },
              },
            ],
          },
          labels: { nodes: [] },
        },
      ];

      const stats = calculateReactionStats(mockIssues);

      expect(stats.total).toBe(2);
      expect(stats.byEmoji["🚀"]).toBe(1);
      expect(stats.byEmoji["👀"]).toBe(1);
    });
  });

  describe("generateDigestMarkdown", () => {
    it("should generate valid markdown digest", async () => {
      const { generateDigestMarkdown } = await import("../bot/handlers/digest-bot.js");

      const stats = {
        total: 100,
        byEmoji: {
          "👍": 50,
          "❤️": 30,
          "🚀": 20,
        },
        byAgent: { "agent-1": 60, "agent-2": 40 },
        blockedIssues: [1, 2],
        escalations: [],
        reviewQueue: [],
        mostActiveAgent: "agent-1",
        mostBlockedRepo: "bug",
      };

      const markdown = generateDigestMarkdown(stats, "Nov 24, 2025");

      expect(markdown).toContain("# 📊 Weekly Agent Emoji Digest (Nov 24, 2025)");
      expect(markdown).toContain("| 👍 | 50 | 50% |");
      expect(markdown).toContain("| ❤️ | 30 | 30% |");
      expect(markdown).toContain("| 🚀 | 20 | 20% |");
      expect(markdown).toContain("**Total Reactions:** 🧮 100");
      expect(markdown).toContain("🔥 Most active agent: `@agent-1`");
      expect(markdown).toContain("❌ Blocked issues: 2");
    });

    it("should handle zero total reactions", async () => {
      const { generateDigestMarkdown } = await import("../bot/handlers/digest-bot.js");

      const stats = {
        total: 0,
        byEmoji: {},
        byAgent: {},
        blockedIssues: [],
        escalations: [],
        reviewQueue: [],
        mostActiveAgent: null,
        mostBlockedRepo: null,
      };

      const markdown = generateDigestMarkdown(stats, "Nov 24, 2025");

      expect(markdown).toContain("# 📊 Weekly Agent Emoji Digest (Nov 24, 2025)");
      expect(markdown).toContain("**Total Reactions:** 🧮 0");
    });
  });

  describe("REACTION_EMOJI_MAP", () => {
    it("should have all expected reaction mappings", async () => {
      const { REACTION_EMOJI_MAP } = await import("../bot/handlers/digest-bot.js");

      expect(REACTION_EMOJI_MAP.THUMBS_UP).toBe("👍");
      expect(REACTION_EMOJI_MAP.THUMBS_DOWN).toBe("👎");
      expect(REACTION_EMOJI_MAP.HEART).toBe("❤️");
      expect(REACTION_EMOJI_MAP.ROCKET).toBe("🚀");
      expect(REACTION_EMOJI_MAP.EYES).toBe("👀");
    });
  });

  describe("postDigestComment", () => {
    it("should post comment to GitHub issue", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 123,
          html_url: "https://github.com/test/test/issues/1#issuecomment-123",
        }),
      });

      const { postDigestComment } = await import("../bot/handlers/digest-bot.js");

      const result = await postDigestComment("owner", "repo", 1, "Test digest");

      expect(result.id).toBe(123);
      expect(mockFetch).toHaveBeenCalledWith(
        "https://api.github.com/repos/owner/repo/issues/1/comments",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ body: "Test digest" }),
        })
      );
    });

    it("should throw error when GITHUB_TOKEN is not set", async () => {
      process.env.GITHUB_TOKEN = "";

      const { postDigestComment } = await import("../bot/handlers/digest-bot.js");

      await expect(
        postDigestComment("owner", "repo", 1, "Test digest")
      ).rejects.toThrow("GITHUB_TOKEN environment variable is not set");
    });
  });
});
