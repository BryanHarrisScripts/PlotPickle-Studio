# HOME — copyable in-chat interactive skeleton (Skin V2)

This is a **reference DIL template**, not a second hosted application or runtime widget. Read `references/surfaces/HOME.md` and current authenticated state before inserting contextual real data. It has five local selections. Keep all five labels and order. `GenUI.issueNewTurn` is invoked only on an actual button click; it is not a storage operation.

```jsx
{@body const [selected,setSelected]=DIL.useState("elara")}
<box theme="dark" background="#100d18" padding={3} radius="xl" gap={3}>
  <row align="center" justify="between">
    <col gap="0"><text weight="semibold">PLOTPICKLE</text><text color="#c1a4e8" size="2xs">STUDIO</text></col>
    <text size="xs">HOME</text>
  </row>
  <text size="xs" color="#bda6eb">YOUR CREATIVE WORKSPACE</text>
  <title size="2xl">What will you create today?</title>
  <text>Your story. Your decisions. Your cut.</text>
  <text color="#c7b7d8" size="sm">Elara works with you right here in ChatGPT.</text>
  <grid minChildWidth={210} gap={3}>
    <grid-item><pressable onClick={()=>setSelected("elara")} background="#241d31" padding={3} radius="lg"><bold>1 · Meet Elara</bold>
Your creative partner for ideas and collaboration.</pressable></grid-item>
    <grid-item><pressable onClick={()=>setSelected("learn")} background="#241d31" padding={3} radius="lg"><bold>2 · Learn</bold>
81 lessons in 12 topics.</pressable></grid-item>
    <grid-item><pressable onClick={()=>setSelected("storyboard")} background="#241d31" padding={3} radius="lg"><bold>3 · Storyboard</bold>
REEL and ONCE storytelling.</pressable></grid-item>
    <grid-item><pressable onClick={()=>setSelected("library")} background="#241d31" padding={3} radius="lg"><bold>4 · Library / Your Stories</bold>
Your private Studio catalogue.</pressable></grid-item>
  </grid>
  <pressable onClick={()=>setSelected("services")} background="#241d31" padding={3} radius="lg"><bold>5 · Connected Services</bold>
Creative tools and integrations.</pressable>
  <box background="#1d1727" padding={3} radius="lg" gap={2}>
    <text size="xs" color="#c2a7f2">SELECTED WORKSPACE</text>
    {#if selected==="elara"}
      <title size="md">Meet Elara</title><text size="sm">Develop an idea together in this conversation.</text><button onClick={()=>GenUI.issueNewTurn("Elara, let's chat in PlotPickle Studio.")}>Chat with Elara</button>
    {:else if selected==="learn"}
      <title size="md">Learn</title><text size="sm">Browse the canonical storytelling curriculum.</text><button onClick={()=>GenUI.issueNewTurn("Elara, show PlotPickle's 81 lessons grouped into 12 topics.")}>Explore lessons</button>
    {:else if selected==="storyboard"}
      <title size="md">Storyboard</title><text size="sm">REEL for film, ONCE for life stories.</text><button onClick={()=>GenUI.issueNewTurn("Elara, open the in-chat Storyboard with REEL and ONCE.")}>Explore Storyboard</button>
    {:else if selected==="library"}
      <title size="md">Library / Your Stories</title><text size="sm">Read my authenticated private Studio catalogue. Do not switch projects.</text><button onClick={()=>GenUI.issueNewTurn("Elara, show my private Studio catalogue and separate source references without switching projects.")}>View stories</button>
    {:else}
      <title size="md">Connected Services</title><text size="sm">Check supported connections without spending credits.</text><button onClick={()=>GenUI.issueNewTurn("Elara, check PlotPickle Connected Services, no media generation or charges.")}>Check services</button>
    {/if}
  </box>
  <text size="xs" color="#aaa0b5">One conversation · One Elara · No automatic project switch</text>
</box>
```

The approved original logo file stays in the plugin at `assets/branding-locked/studio-logo-approved.png`. A text wordmark is a fallback, not a byte-identical replacement. Continue Creating appears only with verified currently loaded state. Do not hardcode private story examples here.

## Branded chat HOME

Render this in the conversation for routine HOME requests and when an explicitly requested interactive panel fails. The approved hosted logo may be displayed where the host supports Markdown images. Keep the heading and link visible even when the image is unavailable. When the host provides in-chat action rows, show the five choices as stacked clickable rows in the same order. Each row sends the existing in-chat navigation request for that choice, such as `PlotPickle Studio: Open Meet Elara`. Offer replies by number or name as well. Use the Markdown list below when those action rows are unavailable. The web link opens the Studio workspace and sits below the five chat choices.

```markdown
![PlotPickle Studio logo](https://plotpickle.avairis.chatgpt.site/assets/studio-logo-approved.png)

**PlotPickle Studio · HOME**

Your story. Your decisions. Your cut.

1. **Meet Elara**
2. **Learn**
3. **Storyboard**
4. **Library / Your Stories**
5. **Connected Services**

Reply with a number or name to continue here.

[Open Studio on the web](https://plotpickle.avairis.chatgpt.site/studio)
```

Use the existing route for the selected choice. Mention the active project only when current signed-in state verifies it. HOME is read-only. An embedded panel remains available on request.
