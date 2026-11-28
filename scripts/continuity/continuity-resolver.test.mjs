import assert from "node:assert/strict";
import test from "node:test";
import { resolveContinuity } from "./continuity-resolver.mjs";

const rule = (id, fields = {}) => ({
  id, projectId: "project", sourceRevision: 3, entityId: "ren", category: "identity",
  attribute: "hair", value: "black", scope: { kind: "project", id: "project" },
  approvalId: "approval", active: true, ...fields,
});
const run = (...rules) => resolveContinuity({
  projectId: "project", revision: 3, entityIds: ["ren", "joy"],
  scopes: { scene: "scene", "mini-block": "mini", shot: "shot" }, rules,
});

test("keeps independent entities and attributes in stable order", () => {
  const rules = [rule("a"), rule("b", { entityId: "joy" }), rule("c", { attribute: "height", value: 172 })];
  assert.equal(run(...rules).resolved.length, 3);
  assert.deepEqual(run(...rules), run(...rules.reverse()));
});

test("rejects conflicting overlapping and same-scope values", () => {
  const scene = rule("a", { scope: { kind: "scene", id: "scene" } });
  const mini = rule("b", { scope: { kind: "mini-block", id: "mini" }, value: "brown" });
  assert.equal(run(scene, mini).conflicts.length, 1);
  assert.equal(run(rule("a"), rule("b", { value: "brown" })).status, "BLOCKED");
});

test("ignores unrelated scopes and retains provenance", () => {
  const shot = rule("shot", { scope: { kind: "shot", id: "shot" }, value: "brown" });
  const other = rule("other", { scope: { kind: "shot", id: "other" } });
  assert.deepEqual(run(rule("a"), shot, other).resolved[0].provenance.map(({ id }) => id), ["shot"]);
});

test("blocks invalid, duplicate and stale rules", () => {
  for (const rules of [[null], [rule("a"), rule("a")], [rule("a", { sourceRevision: 2 })],
    [rule("a", { projectId: "other" })], [rule("a", { approvalId: "" })]]) {
    assert.equal(run(...rules).status, "BLOCKED");
    assert.deepEqual(run(...rules).resolved, []);
  }
});

test("reports unknown for an empty rule set", () => assert.equal(run().status, "UNKNOWN"));
