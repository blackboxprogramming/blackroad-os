// bot/emoji-agent-router.js
// 🔁 Routes emoji to math, status, or escalation handlers

const {
  countEmojis,
  generateHeatmap,
  generateMarkdownReport,
  reactionToCategory,
} = require("./emoji-heatmap");

const {
  emojiToStatus,
  reactionToStatus,
  createProjectStatusSync,
} = require("./project-status-sync");

/**
 * Route types for emoji handling
 */
const ROUTE_TYPES = {
  MATH: "math",
  STATUS: "status",
  ESCALATION: "escalation",
  NOTIFICATION: "notification",
  IGNORE: "ignore",
};

/**
 * Escalation emojis that trigger special handling
 */
const ESCALATION_EMOJIS = ["🛟", "🚨", "🔥"];

/**
 * Emojis that trigger status updates
 */
const STATUS_EMOJIS = ["✅", "🟡", "⬜", "❌", "🔁", "🤔"];

/**
 * Reactions that trigger status updates
 */
const STATUS_REACTIONS = [
  "rocket",
  "hooray",
  "eyes",
  "-1",
  "confused",
];

/**
 * Determine the route type for an emoji
 * @param {string} emoji - The emoji to route
 * @returns {string} - Route type
 */
function determineEmojiRoute(emoji) {
  if (ESCALATION_EMOJIS.includes(emoji)) {
    return ROUTE_TYPES.ESCALATION;
  }
  if (STATUS_EMOJIS.includes(emoji)) {
    return ROUTE_TYPES.STATUS;
  }
  return ROUTE_TYPES.IGNORE;
}

/**
 * Determine the route type for a reaction
 * @param {string} reaction - GitHub reaction name
 * @returns {string} - Route type
 */
function determineReactionRoute(reaction) {
  if (STATUS_REACTIONS.includes(reaction)) {
    return ROUTE_TYPES.STATUS;
  }
  if (reaction === "rotating_light") {
    return ROUTE_TYPES.ESCALATION;
  }
  return ROUTE_TYPES.IGNORE;
}

/**
 * Route context containing all relevant information
 * @typedef {Object} RouteContext
 * @property {string} type - Route type
 * @property {string} emoji - The triggering emoji
 * @property {string|null} status - Status name if applicable
 * @property {boolean} isEscalation - Whether this is an escalation
 * @property {string|null} category - Emoji category
 */

/**
 * Create a route context for an emoji
 * @param {string} emoji - The emoji
 * @returns {RouteContext} - Route context
 */
function createEmojiRouteContext(emoji) {
  const type = determineEmojiRoute(emoji);
  const status = emojiToStatus(emoji);

  return {
    type,
    emoji,
    status,
    isEscalation: type === ROUTE_TYPES.ESCALATION,
    category: null, // Direct emojis don't map to categories
  };
}

/**
 * Create a route context for a reaction
 * @param {string} reaction - GitHub reaction name
 * @returns {RouteContext} - Route context
 */
function createReactionRouteContext(reaction) {
  const type = determineReactionRoute(reaction);
  const status = reactionToStatus(reaction);
  const category = reactionToCategory(reaction);

  return {
    type,
    emoji: reaction, // Store reaction name
    status,
    isEscalation: type === ROUTE_TYPES.ESCALATION,
    category,
  };
}

/**
 * Handler result
 * @typedef {Object} HandlerResult
 * @property {boolean} handled - Whether the event was handled
 * @property {string} action - Action taken
 * @property {Object|null} data - Additional data
 */

/**
 * Create an emoji agent router
 * @param {Object} options - Router options
 * @param {Object} options.octokit - GitHub Octokit instance
 * @param {string} options.projectId - Default project ID
 * @param {Function} options.onEscalation - Escalation callback
 * @param {Function} options.onStatusUpdate - Status update callback
 * @param {Function} options.onMathRequest - Math calculation callback
 * @returns {Object} - Router methods
 */
function createEmojiAgentRouter(options = {}) {
  const {
    octokit,
    projectId,
    onEscalation,
    onStatusUpdate,
    onMathRequest,
  } = options;

  // Create project sync if octokit is available
  const projectSync = octokit
    ? createProjectStatusSync(octokit)
    : null;

  /**
   * Handle an escalation event
   * @param {RouteContext} context - Route context
   * @param {Object} eventData - GitHub event data
   * @returns {Promise<HandlerResult>} - Handler result
   */
  async function handleEscalation(context, eventData) {
    const result = {
      handled: true,
      action: "escalation_triggered",
      data: {
        emoji: context.emoji,
        issueNumber: eventData.issueNumber,
        owner: eventData.owner,
        repo: eventData.repo,
      },
    };

    if (onEscalation) {
      try {
        await onEscalation(context, eventData);
      } catch (error) {
        console.error(`⚠️ Escalation callback error: ${error.message}`);
        result.data.callbackError = error.message;
      }
    }

    console.log(
      `🛟 Escalation triggered for issue #${eventData.issueNumber}`
    );

    return result;
  }

  /**
   * Handle a status update event
   * @param {RouteContext} context - Route context
   * @param {Object} eventData - GitHub event data
   * @returns {Promise<HandlerResult>} - Handler result
   */
  async function handleStatusUpdate(context, eventData) {
    const result = {
      handled: true,
      action: "status_update",
      data: {
        emoji: context.emoji,
        status: context.status,
        issueNumber: eventData.issueNumber,
      },
    };

    // Update project status if sync is available
    if (projectSync && projectId && context.status) {
      try {
        const syncResult = await projectSync.syncIssueStatusFromEmoji({
          owner: eventData.owner,
          repo: eventData.repo,
          issueNumber: eventData.issueNumber,
          emoji: context.emoji,
          projectId,
        });
        result.data.syncResult = syncResult;
      } catch (error) {
        result.data.syncError = error.message;
      }
    }

    if (onStatusUpdate) {
      try {
        await onStatusUpdate(context, eventData);
      } catch (error) {
        console.error(`⚠️ Status update callback error: ${error.message}`);
        result.data.callbackError = error.message;
      }
    }

    console.log(
      `📊 Status update: ${context.status} for issue #${eventData.issueNumber}`
    );

    return result;
  }

  /**
   * Handle a math/calculation request
   * @param {string} text - Text containing emojis
   * @param {Object} options - Options for calculation
   * @returns {HandlerResult} - Handler result
   */
  function handleMathRequest(text, options = {}) {
    const counts = countEmojis(text);
    const heatmap = generateHeatmap(counts);
    const report = options.generateReport
      ? generateMarkdownReport(heatmap, options.title)
      : null;

    const result = {
      handled: true,
      action: "math_calculation",
      data: {
        counts,
        heatmap,
        report,
      },
    };

    if (onMathRequest) {
      onMathRequest(result.data);
    }

    return result;
  }

  /**
   * Route and handle an emoji event
   * @param {string} emoji - The emoji
   * @param {Object} eventData - GitHub event data
   * @returns {Promise<HandlerResult>} - Handler result
   */
  async function routeEmoji(emoji, eventData) {
    const context = createEmojiRouteContext(emoji);

    switch (context.type) {
      case ROUTE_TYPES.ESCALATION:
        return handleEscalation(context, eventData);
      case ROUTE_TYPES.STATUS:
        return handleStatusUpdate(context, eventData);
      default:
        return {
          handled: false,
          action: "ignored",
          data: { emoji, reason: "No handler for emoji" },
        };
    }
  }

  /**
   * Route and handle a reaction event
   * @param {string} reaction - GitHub reaction name
   * @param {Object} eventData - GitHub event data
   * @returns {Promise<HandlerResult>} - Handler result
   */
  async function routeReaction(reaction, eventData) {
    const context = createReactionRouteContext(reaction);

    switch (context.type) {
      case ROUTE_TYPES.ESCALATION:
        return handleEscalation(context, eventData);
      case ROUTE_TYPES.STATUS:
        return handleStatusUpdate(context, eventData);
      default:
        return {
          handled: false,
          action: "ignored",
          data: { reaction, reason: "No handler for reaction" },
        };
    }
  }

  /**
   * Process a batch of emojis for math calculations
   * @param {Array<string>} texts - Array of text to analyze
   * @param {Object} options - Options
   * @returns {HandlerResult} - Handler result with aggregated data
   */
  function processBatchMath(texts, options = {}) {
    const allCounts = texts.map((text) => countEmojis(text));
    const aggregated = allCounts.reduce(
      (acc, counts) => {
        for (const key of Object.keys(acc)) {
          acc[key] += counts[key] || 0;
        }
        return acc;
      },
      {
        completed: 0,
        blocked: 0,
        escalation: 0,
        inProgress: 0,
        review: 0,
        notStarted: 0,
        total: 0,
      }
    );

    const heatmap = generateHeatmap(aggregated);
    const report = options.generateReport
      ? generateMarkdownReport(heatmap, options.title || "Batch Analysis")
      : null;

    return {
      handled: true,
      action: "batch_math_calculation",
      data: {
        itemCount: texts.length,
        aggregatedCounts: aggregated,
        heatmap,
        report,
      },
    };
  }

  return {
    routeEmoji,
    routeReaction,
    handleMathRequest,
    processBatchMath,
    handleEscalation,
    handleStatusUpdate,
    createEmojiRouteContext,
    createReactionRouteContext,
  };
}

module.exports = {
  ROUTE_TYPES,
  ESCALATION_EMOJIS,
  STATUS_EMOJIS,
  STATUS_REACTIONS,
  determineEmojiRoute,
  determineReactionRoute,
  createEmojiRouteContext,
  createReactionRouteContext,
  createEmojiAgentRouter,
};
