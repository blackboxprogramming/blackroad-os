import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import * as fs from "fs";
import * as path from "path";

// Mock fs module
vi.mock("fs", () => ({
  readFileSync: vi.fn(),
  writeFileSync: vi.fn(),
}));

vi.mock("path", async () => {
  const actual = await vi.importActual("path");
  return {
    ...actual,
    join: vi.fn((...args: string[]) => args.join("/")),
  };
});

import {
  readChronicles,
  writeChronicles,
  addEpisode,
  getEpisodeById,
  listEpisodes,
  generateEpisodeMdx,
  getNextEpisodeId,
} from "../src/chronicles";
import type { Chronicles, Episode, EpisodeFrontmatter } from "../src/chronicles/types";

describe("Chronicles", () => {
  const mockChronicles: Chronicles = {
    episodes: [
      {
        id: "episode-001",
        title: "The Clone Awakens",
        agent: "guardian-clone-vault",
        date: "2025-11-23",
        mp3: "https://example.com/audio/guardian-clone-vault.mp3",
        transcript: true,
      },
      {
        id: "episode-002",
        title: "The Digest Protocol",
        agent: "guardian-clone-vault",
        date: "2025-11-24",
        mp3: "https://example.com/audio/guardian-clone-vault.mp3",
        transcript: true,
      },
    ],
  };

  beforeEach(() => {
    vi.mocked(fs.readFileSync).mockReturnValue(JSON.stringify(mockChronicles));
    vi.mocked(fs.writeFileSync).mockClear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("readChronicles", () => {
    it("reads and parses chronicles.json", () => {
      const result = readChronicles();
      expect(result).toEqual(mockChronicles);
      expect(fs.readFileSync).toHaveBeenCalled();
    });
  });

  describe("writeChronicles", () => {
    it("writes chronicles to JSON file", () => {
      writeChronicles(mockChronicles);
      expect(fs.writeFileSync).toHaveBeenCalledWith(
        expect.any(String),
        JSON.stringify(mockChronicles, null, 2) + "\n"
      );
    });
  });

  describe("addEpisode", () => {
    it("adds a new episode to chronicles", () => {
      const newEpisode: Episode = {
        id: "episode-003",
        title: "New Episode",
        agent: "test-agent",
        date: "2025-11-25",
        mp3: "https://example.com/audio/test.mp3",
        transcript: false,
      };

      const result = addEpisode(newEpisode);
      expect(result.episodes).toHaveLength(3);
      expect(result.episodes[2]).toEqual(newEpisode);
      expect(fs.writeFileSync).toHaveBeenCalled();
    });
  });

  describe("getEpisodeById", () => {
    it("returns episode when found", () => {
      const result = getEpisodeById("episode-001");
      expect(result).toEqual(mockChronicles.episodes[0]);
    });

    it("returns undefined when not found", () => {
      const result = getEpisodeById("episode-999");
      expect(result).toBeUndefined();
    });
  });

  describe("listEpisodes", () => {
    it("returns all episodes", () => {
      const result = listEpisodes();
      expect(result).toEqual(mockChronicles.episodes);
    });
  });

  describe("getNextEpisodeId", () => {
    it("returns next episode ID based on count", () => {
      const result = getNextEpisodeId();
      expect(result).toBe("episode-003");
    });
  });

  describe("generateEpisodeMdx", () => {
    it("generates MDX content with frontmatter", () => {
      const frontmatter: EpisodeFrontmatter = {
        id: "episode-003",
        title: "Test Episode",
        agent: "test-agent",
        date: "2025-11-25",
        voice: "/audio/test.mp3",
        transcript: true,
      };
      const narrative = "> **\"This is Lucidia.\"**\n> Test narrative.";

      const result = generateEpisodeMdx(frontmatter, narrative);

      expect(result).toContain("id: episode-003");
      expect(result).toContain('title: "Test Episode"');
      expect(result).toContain("agent: test-agent");
      expect(result).toContain("date: 2025-11-25");
      expect(result).toContain("voice: /audio/test.mp3");
      expect(result).toContain("transcript: true");
      expect(result).toContain(narrative);
      expect(result).toContain("🎧 Listen to the [voice digest]");
      expect(result).toContain("📜 Agent File:");
    });
  });
});
