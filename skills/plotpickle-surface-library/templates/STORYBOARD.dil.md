# STORYBOARD — source-backed responsive in-chat assembly

No source PPF is embedded. Read `studio_get_state` and user-selected source before rendering actual story shots. Equal REEL and ONCE cards are view-only; buttons request in-chat workflow.

```jsx
{@body const [path,setPath]=DIL.useState("REEL")}
<box gap={3}>
  <row align="center" justify="between"><text size="xs">HOME / STORYBOARD</text><button size="sm" variant="outline" onClick={()=>GenUI.issueNewTurn("Home")}>Back</button></row>
  <title size="xl">Storyboard</title><text>Choose how to tell your story.</text>
  <grid columns={2} gap={2}>
    <grid-item><pressable background="surface-secondary" padding={3} radius="lg" onClick={()=>setPath("REEL")}><bold>REEL</bold>
From screenplay to screen.</pressable></grid-item>
    <grid-item><pressable background="surface-secondary" padding={3} radius="lg" onClick={()=>setPath("ONCE")}><bold>ONCE</bold>
Preserve memories and life stories.</pressable></grid-item>
  </grid>
  {#if path==="REEL"}
    <text>New Idea · Import Script · Continue Film · Explore Tools</text>
    <button onClick={()=>GenUI.issueNewTurn("Elara, open REEL in this conversation and show its four starting options without switching projects.")}>Open REEL</button>
  {:else}
    <text>People · Places · Memories · Illustrations · Preserve</text>
    <button onClick={()=>GenUI.issueNewTurn("Elara, open ONCE in this conversation without switching projects.")}>Open ONCE</button>
  {/if}
  <text size="xs">Your Stories — load actual private saved projects before listing them.</text>
  <button variant="outline" onClick={()=>GenUI.issueNewTurn("Elara, show my saved PlotPickle Studio projects, without opening a project.")}>View Your Stories</button>
</box>
```

With verified story loaded: use Skin V1 STORY_MAP and MINI_BLOCK_SHOT_GRID, exact source-backed 25-position 5×5 grid, 5 pages × 5 positions; never treat positions as generated images.
