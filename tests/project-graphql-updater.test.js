// tests/project-graphql-updater.test.js
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("project-graphql-updater", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv, GITHUB_TOKEN: "test-token" };
    mockFetch.mockReset();
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe("updateProjectField", () => {
    it("should update project field successfully", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            updateProjectV2ItemFieldValue: {
              projectV2Item: { id: "item-123" },
            },
          },
        }),
      });

      const { updateProjectField } = await import("../bot/handlers/project-graphql-updater.js");

      const result = await updateProjectField({
        issueNodeId: "issue-node-id",
        projectId: "project-123",
        fieldId: "field-456",
        valueId: "value-789",
      });

      expect(result).toEqual({ id: "item-123" });
      expect(mockFetch).toHaveBeenCalledWith(
        "https://api.github.com/graphql",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer test-token",
          }),
        })
      );
    });

    it("should throw error when GITHUB_TOKEN is not set", async () => {
      process.env.GITHUB_TOKEN = "";

      const { updateProjectField } = await import("../bot/handlers/project-graphql-updater.js");

      await expect(
        updateProjectField({
          issueNodeId: "issue-node-id",
          projectId: "project-123",
          fieldId: "field-456",
          valueId: "value-789",
        })
      ).rejects.toThrow("GITHUB_TOKEN environment variable is not set");
    });

    it("should throw error on GraphQL errors", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          errors: [{ message: "Test error" }],
        }),
      });

      const { updateProjectField } = await import("../bot/handlers/project-graphql-updater.js");

      await expect(
        updateProjectField({
          issueNodeId: "issue-node-id",
          projectId: "project-123",
          fieldId: "field-456",
          valueId: "value-789",
        })
      ).rejects.toThrow("GraphQL errors");
    });
  });

  describe("getIssueNodeId", () => {
    it("should fetch issue node ID successfully", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            repository: {
              issue: { id: "issue-node-123" },
            },
          },
        }),
      });

      const { getIssueNodeId } = await import("../bot/handlers/project-graphql-updater.js");

      const result = await getIssueNodeId("BlackRoad-OS", "blackroad-os", 1);

      expect(result).toBe("issue-node-123");
    });
  });

  describe("getProjectFields", () => {
    it("should fetch project fields successfully", async () => {
      const mockProject = {
        id: "project-123",
        fields: {
          nodes: [
            { id: "field-1", name: "Status", options: [{ id: "opt-1", name: "Done" }] },
          ],
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            user: {
              projectV2: mockProject,
            },
          },
        }),
      });

      const { getProjectFields } = await import("../bot/handlers/project-graphql-updater.js");

      const result = await getProjectFields("BlackRoad-OS", 1);

      expect(result).toEqual(mockProject);
    });
  });
});
