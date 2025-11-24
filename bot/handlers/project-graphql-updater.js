// bot/handlers/project-graphql-updater.js

/**
 * Updates a GitHub Project V2 item field value via GraphQL.
 * Used to change status of project cards when emoji reactions are received.
 */
async function updateProjectField({
  issueNodeId,
  projectId,
  fieldId,
  valueId,
}) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN environment variable is not set");
  }

  const mutation = `
    mutation UpdateProjectField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $valueId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: { singleSelectOptionId: $valueId }
      }) {
        projectV2Item {
          id
        }
      }
    }
  `;

  const variables = {
    projectId,
    itemId: issueNodeId,
    fieldId,
    valueId,
  };

  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: mutation, variables }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`GitHub GraphQL request failed: ${response.status} - ${errorText}`);
  }

  const data = await response.json();

  if (data.errors) {
    throw new Error(`GraphQL errors: ${JSON.stringify(data.errors)}`);
  }

  console.log("✅ Project field updated:", data.data.updateProjectV2ItemFieldValue.projectV2Item.id);
  return data.data.updateProjectV2ItemFieldValue.projectV2Item;
}

/**
 * Fetches the Node ID of an issue by its number.
 */
async function getIssueNodeId(owner, repo, issueNumber) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN environment variable is not set");
  }

  const query = `
    query GetIssueNodeId($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          id
        }
      }
    }
  `;

  const variables = { owner, repo, number: issueNumber };

  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`GitHub GraphQL request failed: ${response.status} - ${errorText}`);
  }

  const data = await response.json();

  if (data.errors) {
    throw new Error(`GraphQL errors: ${JSON.stringify(data.errors)}`);
  }

  return data.data.repository.issue.id;
}

/**
 * Fetches project fields and their options.
 */
async function getProjectFields(owner, projectNumber) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN environment variable is not set");
  }

  const query = `
    query GetProjectFields($owner: String!, $projectNumber: Int!) {
      user(login: $owner) {
        projectV2(number: $projectNumber) {
          id
          fields(first: 20) {
            nodes {
              ... on ProjectV2Field {
                id
                name
              }
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
  `;

  const variables = { owner, projectNumber };

  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`GitHub GraphQL request failed: ${response.status} - ${errorText}`);
  }

  const data = await response.json();

  if (data.errors) {
    throw new Error(`GraphQL errors: ${JSON.stringify(data.errors)}`);
  }

  return data.data.user.projectV2;
}

module.exports = {
  updateProjectField,
  getIssueNodeId,
  getProjectFields,
};
