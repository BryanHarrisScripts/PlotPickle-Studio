---
name: plotpickle-story-workspace
description: At the start of any new PlotPickle story, ask once whether to organize it in a dedicated ChatGPT Project, and guide users to keep later conversations, scripts, images and revisions with that story. Handle returning stories, project names, migration and honest routing status.
---

# Story workspaces — project-first organization (v0.8.13)

A ChatGPT Project is the preferred conversation-and-file home for each distinct story. Do not confuse it with a local output directory, a GitHub repository, a PlotPickle PPF snapshot or the PlotPickle plugin itself. No GitHub account is required. Maintain existing top-level choices (Meet Elara, Learn, Storyboard, Connected Services). This workflow is invoked from Storyboard when a user starts or resumes a named story; it is not a fifth home tab.

## First-time story flow

When a user starts a new story and a matching ChatGPT Project has not been established in the current context, ask *one brief question before building substantial material*:

"Would you like to create a ChatGPT Project called ‘<story title>’ so future conversations, scripts and storyboards stay together?"

Offer: Create project / Use existing project / Continue here. The user can decline without losing access to any PlotPickle features. If already clearly inside the correct project, proceed and do not repeatedly ask. Do not invent a project list or claim to have searched the user's sidebar when not available. For an unnamed story, ask for a title only when required; don't block a brainstorming conversation to force naming or project creation. Allow renames without silently duplicating projects.

If the user chooses Create project: when an explicit authorized host tool can create a ChatGPT Project, use it and verify its returned identity. Otherwise, guide the user to ChatGPT sidebar > New project > enter the story title and choose an icon/color, then open a *new chat inside that project* and invoke PlotPickle there. Explicitly say the plugin itself has **not** created the ChatGPT Project. When an existing conversation is eligible, the user may use its menu > Move to project (or drag it to the project); do not assume every chat is eligible. Do not pretend moving a chat carries over local files; attach story sources to the new project as appropriate.

If the user chooses Use existing project: ask the name only if unknown, then guide them to open it and start future PlotPickle work there. If the title matches multiple stories, ask which project to use. Never silently merge stories or claim to move conversations.

If the user chooses Continue here: continue without a warning loop; optionally prepare a portable story directory and bundle exports only when requested. Keep the option available for later.

## Subsequent conversations and routing

- On return to a named story, identify the intended story using the active project and actually accessible source files. Memory and previous chat summaries are contextual clues only; they are not proof of the current project, file state or story identity.
- If the user appears to be working outside the established story project, gently offer "Continue in your <story title> ChatGPT Project" before writing new durable story output. Do not block simple discussion.
- The plugin **cannot automatically intercept, relocate or retag future ChatGPT conversations** using its packaged skills. Future chats stay organized when the user starts them within the matching ChatGPT Project. Never promise background auto-routing, silently create a Project or claim persistence without supported API/action evidence.
- If the host in a future version supplies a trustworthy current-project identifier and authorized create/move action, route only with user consent, confirm results and fail closed on errors. Never invent IDs/URLs.
- Store changes only through actual authorized persistent file/project operations. A generated download under `/mnt/data` is a session artifact, **not** a ChatGPT Project source until attached or saved to that Project.
- Keep a story's screenplay, outlines, characters, world guides, shot plans, image assets, Previs outputs, poster packs, exported PPF and revision notes together logically; distinguish source material from generated drafts and approved versions.
- When working with exported files, preserve stable project IDs and source fingerprints from `../read-plotpickle-project/SKILL.md`. A project rename must not reset Save/Lock, continuity or identity.

## Example — The Third Bell

The suggested ChatGPT Project is "The Third Bell". The user's current screenplay and Block 1.1 storyboard package are existing artifacts; do not claim they were uploaded to, locked by, or organized within a ChatGPT Project unless a current operation proves it. If the user creates that project, instruct them to add the original story treatment, screenplay draft, shot board and 25-image bundle as project sources when useful, subject to their file limits. For subsequent discussions they should open "The Third Bell", start a chat there and call PlotPickle. This is a guided process, not automatic chat migration.

## User-facing status words

Use honest status descriptions: "Project proposed", "User-created project (reported)", "Project verified by host" or "Chat not moved". Never label "Project created" or "Chats routed" because a folder was created on the local filesystem or because a title exists in the conversation. Check actual host evidence before marking an operation complete.
