// bot/handlers/project-status-sync.js
// Handler for syncing project statuses based on emoji reactions

const STATUS_MAP = {
  "✅": "Done",
  "🟡": "In Progress",
  "⬜": "Not Started",
  "❌": "Blocked",
  "🔁": "Rework",
  "🤔": "Needs Review",
  "🛟": "Escalation"
};

/**
 * Map emoji to project status
 * @param {string} emoji - The emoji character
 * @returns {string|null} - The corresponding status or null if not found
 */
function mapEmojiToStatus(emoji) {
  return STATUS_MAP[emoji] || null;
}

/**
 * Map reaction name to project status
 * @param {string} reaction - The reaction name (e.g., "rocket", "eyes")
 * @returns {string|null} - The corresponding status or null if not found
 */
function mapReactionToStatus(reaction) {
  const REACTION_MAP = {
    hooray: "Done",
    rocket: "Done",
    eyes: "In Progress",
    "+1": "Done",
    "-1": "Blocked",
    confused: "Blocked",
    thinking_face: "Needs Review",
    rotating_light: "Escalation"
  };
  return REACTION_MAP[reaction] || null;
}

/**
 * Get all status mappings
 * @returns {Object} - All emoji to status mappings
 */
function getStatusMappings() {
  return { ...STATUS_MAP };
}

/**
 * Sync project status based on reaction
 * @param {Object} options - Sync options
 * @param {string} options.reaction - The reaction name
 * @param {string|number} options.issueId - The issue or PR ID
 * @param {string|number} options.projectId - The project ID
 * @returns {Object} - Sync result
 */
async function syncProjectStatus({ reaction, issueId, projectId }) {
  const status = mapReactionToStatus(reaction);
  
  if (!status) {
    return {
      success: false,
      message: `No status mapping for reaction: ${reaction}`
    };
  }

  // This would be implemented with actual GitHub GraphQL API calls
  // For now, return the intended status change
  return {
    success: true,
    issueId,
    projectId,
    newStatus: status,
    reaction,
    message: `Status would be updated to: ${status}`
  };
}

module.exports = {
  mapEmojiToStatus,
  mapReactionToStatus,
  getStatusMappings,
  syncProjectStatus
};
