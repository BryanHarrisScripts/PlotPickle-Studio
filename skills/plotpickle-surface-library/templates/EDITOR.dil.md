# EDITOR — registered draft visualization only

**Not an approved Skin V2 visual lock.** Hydrate from actual `studio_get_state` and show real clips/cues/frame counts or a clear empty state. Do not fabricate waveform/drag/play/MP4. Every editing or render operation requires a new explicit turn, real backend action and readback.

```jsx
{@body const [lane,setLane]=DIL.useState("video")}
<box gap={3}>
  <row align="center" justify="between"><text size="xs">HOME / STORYBOARD / EDITOR</text><button size="sm" variant="outline" onClick={()=>GenUI.issueNewTurn("Elara, return to Storyboard without editing my timeline.")}>Back</button></row>
  <title size="xl">Editor</title>
  <text size="xs" color="secondary">24 fps · Six-lane timeline · Project/source state must be verified</text>
  <radio-group value={lane} onChange={setLane} direction="col">
    <radio value="video">Video</radio>
    <radio value="dialogue">Dialogue</radio>
    <radio value="action">Action</radio>
    <radio value="foley">Foley</radio>
    <radio value="ambience">Ambience</radio>
    <radio value="music">Music</radio>
  </radio-group>
  <box background="surface-secondary" radius="lg" padding={3}><text size="sm">Selected lane: {lane}. Source clips/cues appear only after authenticated timeline read.</text></box>
  <row wrap="wrap" gap={2}><button variant="outline" onClick={()=>GenUI.issueNewTurn("Elara, inspect the current PlotPickle six-track timeline read-only, and report its real 24 fps frame count and revision.")}>Inspect timeline</button><button variant="outline" onClick={()=>GenUI.issueNewTurn("Elara, prepare a read-only render plan and verify the exact current timeline fingerprint. Do not execute a render.")}>Check render plan</button></row>
</box>
```

`Render Draft` requires explicit user request, current media source checks, real execution and MP4 readback. This draft surface cannot approve a master.
