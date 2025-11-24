// bot/handlers/project-graphql-updater.js

/**
 * Updates a GitHub Project V2 field value via GraphQL.
 * Used to change the status of linked project cards when reactions are triggered.
 */
async function updateProjectField({
  issueNodeId,
  projectId,
  fieldId,
  valueId,
}) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN environment variable is required");
  }

  const mutation = `
    mutation UpdateProjectV2ItemFieldValue($input: UpdateProjectV2ItemFieldValueInput!) {
      updateProjectV2ItemFieldValue(input: $input) {
        projectV2Item {
          id
        }
      }
    }
  `;

  const variables = {
    input: {
      projectId,
      itemId: issueNodeId,
      fieldId,
      value: { singleSelectOptionId: valueId },
    },
  };

  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query: mutation, variables }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`GraphQL request failed: ${response.status} - ${error}`);
  }

  const result = await response.json();

  if (result.errors) {
    throw new Error(`GraphQL errors: ${JSON.stringify(result.errors)}`);
  }

  console.log("✅ Project field updated:", result.data);
  return result.data;
}

/**
 * Fetches the Node ID for an issue, project details, and field options.
 * Useful for obtaining the required IDs before calling updateProjectField.
 */
async function fetchProjectMetadata({ owner, repo, issueNumber, projectNumber }) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN environment variable is required");
  }

  const query = `
    query FetchProjectMetadata($owner: String!, $repo: String!, $issueNumber: Int!, $projectNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          id
        }
      }
      user(login: $owner) {
        projectV2(number: $projectNumber) {
          id
          fields(first: 20) {
            nodes {
              ... on ProjectV2FieldCommon {
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

  const variables = { owner, repo, issueNumber, projectNumber };

  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`GraphQL request failed: ${response.status} - ${error}`);
  }

  const result = await response.json();

  if (result.errors) {
    throw new Error(`GraphQL errors: ${JSON.stringify(result.errors)}`);
  }

  return result.data;
}

module.exports = {
  updateProjectField,
  fetchProjectMetadata,
};
