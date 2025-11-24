const routeEmoji = require("./handlers/emoji-agent-router");

async function handleReaction(payload) {
  const reaction = payload?.reaction?.emoji?.name;

  if (reaction) {
    await routeEmoji({
      emoji: reaction,
      repo: "BlackRoad-OS/blackroad-os-api",
      issue: payload.issue,
    });
  }
}

module.exports = { handleReaction };
