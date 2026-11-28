const categories = new Set([
  "identity", "wardrobe", "prop", "architecture", "palette", "time", "weather", "camera",
]);

const scopeRanks = new Map([
  ["project", 0], ["sequence", 1], ["block", 2],
  ["mini-block", 3], ["scene", 3], ["shot", 4],
]);

const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0;
const validId = (value) => typeof value === "string" && value.length > 0 && value.trim() === value;
const validValue = (value) => typeof value === "string" ||
  typeof value === "boolean" || Number.isFinite(value);

/**
 * Resolve rules already vetted by the canonical approval reader.
 * Scope addresses must come from the authoritative shot record.
 * A null entityId denotes an explicitly project-wide rule.
 */
export function resolveContinuity({ projectId, revision, entityIds, scopes, rules }) {
  const entities = new Set(entityIds);
  const seen = new Set();
  const groups = new Map();
  const invalid = [];

  for (const rule of rules) {
    if (!validId(rule?.id) || seen.has(rule.id) || rule.projectId !== projectId ||
        !categories.has(rule.category) || !validId(rule.attribute) ||
        !validValue(rule.value) || !scopeRanks.has(rule.scope?.kind) ||
        !validId(rule.scope.id) || (rule.scope.kind === "project" && rule.scope.id !== projectId) ||
        (rule.entityId !== null && !validId(rule.entityId)) || typeof rule.active !== "boolean") {
      invalid.push(validId(rule?.id) ? rule.id : null);
      continue;
    }
    seen.add(rule.id);
    if (!rule.active || (rule.entityId !== null && !entities.has(rule.entityId)) ||
        (rule.scope.kind !== "project" && scopes[rule.scope.kind] !== rule.scope.id)) {
      continue;
    }
    if (!validId(rule.approvalId) || rule.sourceRevision !== revision) {
      invalid.push(rule.id);
      continue;
    }
    const key = JSON.stringify([rule.entityId, rule.category, rule.attribute]);
    const group = groups.get(key) ?? [];
    group.push(rule);
    groups.set(key, group);
  }

  if (invalid.length > 0) {
    return { status: "BLOCKED", resolved: [], conflicts: [], invalid: invalid.sort((a, b) => compare(a ?? "", b ?? "")) };
  }

  const resolved = [];
  const conflicts = [];
  for (const [key, group] of [...groups].sort(([a], [b]) => compare(a, b))) {
    const highest = Math.max(...group.map((rule) => scopeRanks.get(rule.scope.kind)));
    const candidates = group.filter((rule) => scopeRanks.get(rule.scope.kind) === highest);
    candidates.sort((a, b) => compare(a.id, b.id));
    const [entityId, category, attribute] = JSON.parse(key);
    const provenance = candidates.map(({ id, scope, approvalId }) => ({ id, scope, approvalId }));
    const entry = { entityId, category, attribute, provenance };
    if (candidates.some((rule) => rule.value !== candidates[0].value)) {
      conflicts.push(entry);
    } else {
      resolved.push({ ...entry, value: candidates[0].value });
    }
  }

  return {
    status: conflicts.length > 0 ? "BLOCKED" : resolved.length > 0 ? "RESOLVED" : "UNKNOWN",
    resolved,
    conflicts,
    invalid,
  };
}
