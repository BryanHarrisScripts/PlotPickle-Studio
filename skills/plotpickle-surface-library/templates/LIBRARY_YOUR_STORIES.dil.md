# LIBRARY / YOUR STORIES — live catalogue, not synthetic list

Before building the actual card, call authenticated `studio_list_projects` and `studio_get_state`. Construct the two groups from those results only. Below is a safe empty-state reference. Replace the empty-state text with **real bound data** when present; do not paste example project titles into this template.

```jsx
<box gap={3}>
  <row justify="between" align="center"><text size="xs">HOME / LIBRARY / YOUR STORIES</text><button size="sm" variant="outline" onClick={()=>GenUI.issueNewTurn("Home")}>Back</button></row>
  <title size="xl">Library / Your Stories</title>
  <text>Private saved Studio catalogue</text>
  <box background="surface-secondary" padding={3} radius="lg"><bold>Saved Studio projects</bold>
Display only authenticated catalogue results. No project is opened by viewing this section.</box>
  <box background="surface-secondary" padding={3} radius="lg"><bold>Source references needing verification</bold>
Display only registry entries labeled as unverified. Source references are not automatically loadable projects.</box>
  <Link url="https://chatgpt.com/library" title="Open ChatGPT Library">Open ChatGPT Library</Link>
  <text size="xs">No automatic Library-wide scan. Selection is not approval.</text>
</box>
```

For each real saved Studio project, its **Open** button must submit an exact project selection turn with project identity (from tool output), then Elara calls `studio_check_project`, rereads current revision, guarded `studio_open_project`, and independently verifies readback. The templates themselves never embed a user's project ID or hash.
