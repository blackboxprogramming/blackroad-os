// bot/emoji-agent-router.js
// Routes emoji reactions to appropriate agent handlers

const AGENT_ROUTES = {
  // Status change reactions
  "✅": { agent: "status-agent", action: "mark_done" },
  "🟡": { agent: "status-agent", action: "mark_in_progress" },
  "⬜": { agent: "status-agent", action: "mark_not_started" },
  "❌": { agent: "status-agent", action: "mark_blocked" },
  "🔁": { agent: "status-agent", action: "mark_rework" },
  
  // Special agent triggers
  "🤔": { agent: "review-agent", action: "request_review" },
  "🛟": { agent: "guardian-agent", action: "escalate" },
  "🤖": { agent: "auto-assign-agent", action: "auto_assign" },
  "🧍‍♀️": { agent: "assignment-agent", action: "assign_human" },
  "👥": { agent: "team-agent", action: "tag_team" }
};

// Reaction name to emoji mapping for GitHub reactions
const REACTION_TO_EMOJI = {
  "+1": "👍",
  "-1": "👎",
  laugh: "😄",
  hooray: "🎉",
  confused: "😕",
  heart: "❤️",
  rocket: "🚀",
  eyes: "👀"
};

// Reaction name to agent routing
const REACTION_ROUTES = {
  hooray: { agent: "status-agent", action: "mark_done" },
  rocket: { agent: "status-agent", action: "mark_done" },
  eyes: { agent: "status-agent", action: "mark_in_progress" },
  "+1": { agent: "status-agent", action: "approve" },
  "-1": { agent: "status-agent", action: "mark_blocked" },
  confused: { agent: "status-agent", action: "mark_blocked" }
};

/**
 * Route an emoji to the appropriate agent
 * @param {string} emoji - The emoji character
 * @returns {Object|null} - Agent routing info or null if not found
 */
function routeEmoji(emoji) {
  return AGENT_ROUTES[emoji] || null;
}

/**
 * Route a reaction name to the appropriate agent
 * @param {string} reaction - The reaction name (e.g., "rocket")
 * @returns {Object|null} - Agent routing info or null if not found
 */
function routeReaction(reaction) {
  return REACTION_ROUTES[reaction] || null;
}

/**
 * Get all registered emoji routes
 * @returns {Object} - All emoji routes
 */
function getEmojiRoutes() {
  return { ...AGENT_ROUTES };
}

/**
 * Get all registered reaction routes
 * @returns {Object} - All reaction routes
 */
function getReactionRoutes() {
  return { ...REACTION_ROUTES };
}

/**
 * Convert a reaction name to its emoji representation
 * @param {string} reaction - The reaction name
 * @returns {string|null} - The emoji or null if not found
 */
function reactionToEmoji(reaction) {
  return REACTION_TO_EMOJI[reaction] || null;
}

/**
 * Process an incoming reaction and return handling instructions
 * @param {Object} options - Processing options
 * @param {string} options.reaction - The reaction name
 * @param {Object} options.payload - The event payload
 * @returns {Object} - Processing result with routing info
 */
function processReaction({ reaction, payload }) {
  const route = routeReaction(reaction);
  
  if (!route) {
    return {
      handled: false,
      reason: `No route for reaction: ${reaction}`
    };
  }

  return {
    handled: true,
    agent: route.agent,
    action: route.action,
    reaction,
    emoji: reactionToEmoji(reaction),
    issueNumber: payload?.issue?.number || payload?.pull_request?.number,
    repository: payload?.repository?.full_name
  };
}

module.exports = {
  routeEmoji,
  routeReaction,
  getEmojiRoutes,
  getReactionRoutes,
  reactionToEmoji,
  processReaction,
  AGENT_ROUTES,
  REACTION_ROUTES
};
