# REVIEW — inspect exact selected source version

Render only after verifying actual selected user-owned image bytes and current source. This is the **empty/unverified state** skeleton. Hydrate with genuine image, variant list and independent approval/media evidence. Navigation and evidence tabs are local; actions submit explicit turns for guarded tools.

```jsx
{@body const [tab,setTab]=DIL.useState("Script")}
<box gap={3}>
  <row align="center" justify="between"><text size="xs">HOME / STORYBOARD / REVIEW</text><button size="sm" variant="outline" onClick={()=>GenUI.issueNewTurn("Elara, return to Storyboard without changing my story.")}>Back</button></row>
  <title size="xl">Image Review</title>
  <box background="surface-secondary" padding={4} radius="lg"><text color="secondary">Selected image unavailable until exact source bytes are verified.</text></box>
  <text size="xs">Human Approved: Unknown · PPF Saved: Unknown · PPF Locked: Unknown · Media Verified: Unknown</text>
  <segmented-control value={tab} onChange={setTab} options={[{"label":"Script","value":"Script"},{"label":"Prompt","value":"Prompt"},{"label":"Continuity","value":"Continuity"},{"label":"Audit","value":"Audit"}]}/>
  <text color="secondary" size="sm">{tab} details require the verified selected source.</text>
  <button variant="outline" onClick={()=>GenUI.issueNewTurn("Elara, show me my currently selected shot and exact media evidence in read-only mode before we discuss approval.")}>Review with Elara</button>
</box>
```

Do not activate Save/Lock/Unlock/Regenerate as a direct UI status toggle. A real action must be a new intent turn plus exact hash/revision verification, guarded writer and independent readback. No speculative private image rendering.
