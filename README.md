# PlotPickle Studio

<p align="center">
  <img src="assets/studio-logo.png" alt="PlotPickle Studio" width="320">
</p>

**Your story. Your decisions. Your cut.**

**Open-source ChatGPT plugin**

PlotPickle Studio is an open-source project available for personal installation and community testing through ChatGPT’s **Plugins → Personal** area. This repository provides source code, documentation and downloadable releases. Access depends on ChatGPT account permissions and the Studio connection. Published material is governed by its applicable licence.

PlotPickle Studio is a storytelling learning and creative development plugin for students, hobbyists and independent storytellers. Work with Elara, your creative collaborator, to learn the craft, experiment visually through trial and error, and develop a better story.

The goal is not to produce a perfect movie. It is to help you explore what works, refine your creative vision and build a compelling pitch package for a book, comic book, short story, feature-length film or episodic series.

**[Website](https://plotpickle.com)** · [Studio](https://studio.plotpickle.com/home) · [Downloads](https://github.com/BryanHarrisScripts/PlotPickle-Studio/releases)

- **Learn** — explore an expanding library of storytelling and creative development lessons.
- **Experiment** — visualize ideas, characters, worlds and scenes; compare alternatives through trial and error.
- **Develop** — refine narrative, structure, dialogue, pacing and visual continuity with Elara.
- **Pitch** — assemble written, illustrated or cinematic materials that communicate your story and creative vision.

<p align="center">
  <img src="assets/plotpickle-creative-workflow.svg" alt="PlotPickle Studio: learn, experiment, develop and pitch; the creative process is iterative and the creator retains control" width="100%">
</p>

## A system that grows with you

Choose **REEL** to develop a fictional story or **ONCE** to explore personal memories and life stories. Both encourage learning by doing. The curriculum and Elara's creative guidance can expand as storytelling techniques, research and AI capabilities evolve.

## Surface sitemap

```text
PLOTPICKLE STUDIO — in this ChatGPT conversation
├── HOME — Skin V2, five cards in this order
│   ├── 1. MEET ELARA — creative collaboration in chat
│   ├── 2. LEARN — 12 topics → 81 lessons
│   ├── 3. STORYBOARD
│   │   ├── REEL — film / screenplay route
│   │   └── ONCE — personal story route
│   ├── 4. LIBRARY / YOUR STORIES
│   │   ├── Signed-in Studio project catalogue
│   │   └── Select source files in chat or import PPF/WebP from HOME
│   └── 5. CONNECTED SERVICES
│       ├── PlotPickle Studio
│       └── ChatGPT Space
└── DIRECT STUDIO ENTRY POINTS
    ├── STORY MAP — 4 Acts → 12 Sequences → 24 Blocks → 96 Mini-Blocks
    ├── SHOT GRID — 25 planning positions per Mini-Block
    ├── REVIEW / EDITOR — shot review and six-track timeline
    │   └── PITCH EDIT — timeline workflow
    └── SYSTEM RECORDS — account-private Studio records inventory
```

## Developer architecture

PlotPickle separates its creative core from the infrastructure that runs it. The aim is portability through host-specific integrations, not dependence on a particular model or platform. The current implementation has limitations; other potential hosts remain untested.

The architecture includes two complementary feedback loops: the creator learns through visual experimentation, while PlotPickle can improve through reviewed research, open-source discovery (OSS Radar), optional feedback and tested releases. System improvements are proposals until reviewed and approved; private stories are not automatically collected for training or used to change the system.

<p align="center">
  <img src="assets/plotpickle-developer-architecture.svg" alt="PlotPickle developer architecture: creative core, host adapters, AI infrastructure, optional tools and two feedback loops for human learning and reviewed system evolution" width="100%">
</p>

## Version 2.0.61

The private ChatGPT plugin includes 37 skills, Animation & Motion Intelligence V1 and the read-only `/systemhealth` report. The 2.0.61 hosted worker serves the marketing site, Studio and MCP.

Start with `Home` in Chat. Ask for `Story Map`, `Shot Grid`, `Review`, `Editor`, or `Pitch Package` as you develop your story. Elara connects to the signed-in Studio working copy over MCP using ChatGPT OAuth. The workflow saves a candidate, reopens it to verify the saved record, then locks it with creator approval and verifies the lock. Studio Learn offers 81 lessons across 12 topics.

Ask Elara for `Animation`, `MotionBrief`, `MotionReview`, `Emotion`, `Continuity`, or `Director` guidance. The motion skill adds twelve knowledge modules, provider-independent planning, and a supplemental animation lesson. Read the [skill](skills/plotpickle-animation-motion-v1/SKILL.md) and [supplement](skills/plotpickle-animation-motion-v1/learn.md).

<details>
<summary>37 plugin skills</summary>

- [plotpickle-animatic](skills/plotpickle-animatic/SKILL.md)
- [plotpickle-animation-motion-v1](skills/plotpickle-animation-motion-v1/SKILL.md)
- [plotpickle-approval](skills/plotpickle-approval/SKILL.md)
- [plotpickle-approval-truth](skills/plotpickle-approval-truth/SKILL.md)
- [plotpickle-assets](skills/plotpickle-assets/SKILL.md)
- [plotpickle-chat-first](skills/plotpickle-chat-first/SKILL.md)
- [plotpickle-community](skills/plotpickle-community/SKILL.md)
- [plotpickle-creative](skills/plotpickle-creative/SKILL.md)
- [plotpickle-design](skills/plotpickle-design/SKILL.md)
- [plotpickle-editor](skills/plotpickle-editor/SKILL.md)
- [plotpickle-fal-player](skills/plotpickle-fal-player/SKILL.md)
- [plotpickle-fal-production](skills/plotpickle-fal-production/SKILL.md)
- [plotpickle-graphic-novel](skills/plotpickle-graphic-novel/SKILL.md)
- [plotpickle-image-production](skills/plotpickle-image-production/SKILL.md)
- [plotpickle-interactive-storyboard](skills/plotpickle-interactive-storyboard/SKILL.md)
- [plotpickle-naming](skills/plotpickle-naming/SKILL.md)
- [plotpickle-navigator](skills/plotpickle-navigator/SKILL.md)
- [plotpickle-official-reader](skills/plotpickle-official-reader/SKILL.md)
- [plotpickle-oss-radar](skills/plotpickle-oss-radar/SKILL.md)
- [plotpickle-pitch-deck](skills/plotpickle-pitch-deck/SKILL.md)
- [plotpickle-posters](skills/plotpickle-posters/SKILL.md)
- [plotpickle-produce](skills/plotpickle-produce/SKILL.md)
- [plotpickle-release-lock](skills/plotpickle-release-lock/SKILL.md)
- [plotpickle-reports](skills/plotpickle-reports/SKILL.md)
- [plotpickle-review](skills/plotpickle-review/SKILL.md)
- [plotpickle-site-retirement](skills/plotpickle-site-retirement/SKILL.md)
- [plotpickle-skin-v1](skills/plotpickle-skin-v1/SKILL.md)
- [plotpickle-skin-v2](skills/plotpickle-skin-v2/SKILL.md)
- [plotpickle-story-flow](skills/plotpickle-story-flow/SKILL.md)
- [plotpickle-story-workspace](skills/plotpickle-story-workspace/SKILL.md)
- [plotpickle-studio](skills/plotpickle-studio/SKILL.md)
- [plotpickle-surface-library](skills/plotpickle-surface-library/SKILL.md)
- [plotpickle-transfer](skills/plotpickle-transfer/SKILL.md)
- [plotpickle-truth-gate](skills/plotpickle-truth-gate/SKILL.md)
- [plotpickle-unified-application](skills/plotpickle-unified-application/SKILL.md)
- [plotpickle-welcome](skills/plotpickle-welcome/SKILL.md)
- [read-plotpickle-project](skills/read-plotpickle-project/SKILL.md)

</details>

## Install in ChatGPT

1. Sign in to [ChatGPT](https://chatgpt.com/) with the account you want to use.
2. Open **Plugins → Personal**. Under **Created by you**, select **PlotPickle Studio** if it is already listed.
3. Select **Install plugin** or the **+** button if shown. If prompted to connect to Studio, review the permissions and follow the ChatGPT sign-in prompts.
4. Start a conversation, type `@PlotPickle Studio`, select the plugin, and ask **Open Studio HOME**.

### Set up from a ZIP

Download the latest published package from [GitHub Releases](https://github.com/BryanHarrisScripts/PlotPickle-Studio/releases). Setup depends on account permissions and Studio connection access.

1. Open the release page above and download the plugin ZIP from **Assets** (not GitHub's automatically generated source-code ZIP).
2. Compare the ZIP's SHA-256 checksum with the checksum supplied with the release.
3. In ChatGPT, open **Plugins → Add** and select **Plugin Creator**, if available. Install it if prompted.
4. Attach the downloaded ZIP in a Plugin Creator conversation and ask it to create PlotPickle Studio as a personal plugin.
5. Open **Plugins → Personal**, select PlotPickle Studio and install it. Review and authorize the Studio connection if prompted.
6. Start a conversation, select `@PlotPickle Studio` and ask **Open Studio HOME**.

The v2.0.57 and v2.0.58 releases are superseded by v2.0.59. The archived v2.0.55 ZIP uses a retired Studio connection and should not be used for new installations. For future updates, check [GitHub Releases](https://github.com/BryanHarrisScripts/PlotPickle-Studio/releases/latest).

The v2.0.59 release includes a plugin ZIP and SHA-256 checksum. Connected Services lists PlotPickle Studio and ChatGPT Space; optional providers are managed through their own ChatGPT plugins. Save → Lock is designed to verify the exact PPF and original image in the private Studio working copy. Release notes report passing automated checks; signed-in production acceptance remains pending. Setup depends on account permissions and access to the Studio connection.

[OpenAI’s plugin installation and setup instructions](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt)

For release packaging and verification, see [RELEASES.md](RELEASES.md).

## Licensing

**[Open Technology](docs/licensing/OPEN-TECHNOLOGY.md)** — MIT-licensed designated software may be used, modified and redistributed for personal or commercial purposes, subject to preserving the copyright and licence notices.

**[Shared Creativity](docs/licensing/SHARED-CREATIVITY.md)** — designated creative and educational works are licensed under CC BY-NC-SA 4.0: sharing and adaptation are permitted for noncommercial purposes with attribution and the same licence for adaptations.

The licence supplied with each published file or release governs that material. User stories remain under their creators’ chosen terms.

**The human remains the author.**
