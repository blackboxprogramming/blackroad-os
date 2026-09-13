// Registry identities are canonical ASCII hostnames, never URLs. These checks
// are local namespace validation; they make no DNS, ownership, or health claim.
const LABEL = /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/;

export function isCanonicalHostname(value) {
  if (typeof value !== "string" || value.length > 253 || /[^a-z0-9.-]/.test(value)) return false;
  const labels = value.split(".");
  return labels.length >= 2 && labels.every((label) => LABEL.test(label)) && /^[a-z]/.test(labels.at(-1));
}

export function domainIdentityErrors(names) {
  const errors = [];
  const unique = new Set();
  for (const [index, name] of names.entries()) {
    if (!isCanonicalHostname(name)) {
      errors.push(`domains[${index}].name must be a canonical hostname (lowercase ASCII, valid labels, no URL or trailing dot)`);
      continue;
    }
    if (unique.has(name)) errors.push(`duplicate domain name "${name}"`);
    for (const other of unique) {
      if (name.endsWith("." + other) || other.endsWith("." + name)) {
        errors.push(`overlapping root domains "${other}" and "${name}"`);
      }
    }
    unique.add(name);
  }
  return errors;
}

export function registeredRoot(hostname, roots) {
  if (!isCanonicalHostname(hostname)) return null;
  const matches = roots.filter((root) => isCanonicalHostname(root) && (hostname === root || hostname.endsWith("." + root)));
  return matches.length === 1 ? matches[0] : null;
}
