// bot/index.js

console.log("🤖 Emoji Bot Activated");

const event = process.env.GITHUB_EVENT_PATH;
const fs = require("fs");
const { updateProjectField, getIssueNodeId } = require("./handlers/project-graphql-updater");

// Load configuration
const configPath = process.env.EMOJI_BOT_CONFIG || "../emoji-bot-config.yml";

// Mapping of reaction content to status updates
const REACTION_TO_STATUS = {
  eyes: "Done",
  hooray: "Done",
  rocket: "Done",
  "+1": "Done",
  "-1": "Blocked",
  confused: "Blocked",
  thinking_face: "Needs Review",
};

if (!event || !fs.existsSync(event)) {
  console.error("🚫 No GitHub event payload found.");
  process.exit(1);
}

const payload = JSON.parse(fs.readFileSync(event, "utf8"));
console.log("📦 Event Payload:", JSON.stringify(payload, null, 2));

const reaction = payload.reaction?.content || "";

/**
 * Updates the GitHub Project card status based on reaction.
 * Requires PROJECT_ID, STATUS_FIELD_ID, and status option IDs to be set.
 */
async function handleProjectUpdate(statusName) {
  const projectId = process.env.PROJECT_ID;
  const fieldId = process.env.STATUS_FIELD_ID;
  const statusOptions = process.env.STATUS_OPTIONS ? JSON.parse(process.env.STATUS_OPTIONS) : {};
  const valueId = statusOptions[statusName];

  if (!projectId || !fieldId || !valueId) {
    console.log("⚠️ Project update skipped: missing PROJECT_ID, STATUS_FIELD_ID, or STATUS_OPTIONS");
    return;
  }

  const issueNumber = payload.issue?.number;
  const owner = payload.repository?.owner?.login;
  const repo = payload.repository?.name;

  if (!issueNumber || !owner || !repo) {
    console.log("⚠️ Project update skipped: missing issue/repo information");
    return;
  }

  try {
    const issueNodeId = await getIssueNodeId(owner, repo, issueNumber);
    await updateProjectField({ issueNodeId, projectId, fieldId, valueId });
    console.log(`🎯 Project status updated to: ${statusName}`);
  } catch (error) {
    console.error("❌ Failed to update project:", error.message);
  }
}

if (reaction) {
  console.log(`🧠 Reaction received: ${reaction}`);

  const statusName = REACTION_TO_STATUS[reaction];

  switch (reaction) {
    case "eyes":
      console.log("👀 Mark as Done");
      break;
    case "hooray":
    case "rocket":
    case "+1":
      console.log("✅ Mark as Done");
      break;
    case "-1":
    case "confused":
      console.log("❌ Mark as Blocked");
      break;
    case "rotating_light":
      console.log("🛟 Escalation triggered");
      break;
    case "thinking_face":
      console.log("🤔 Needs Review assigned");
      break;
    default:
      console.log("🪞 No mapping for this reaction.");
  }

  // Trigger project update if status mapping exists
  if (statusName) {
    handleProjectUpdate(statusName).catch(console.error);
  }
} else {
  console.log("💬 Comment ignored — no emoji trigger detected.");
}
