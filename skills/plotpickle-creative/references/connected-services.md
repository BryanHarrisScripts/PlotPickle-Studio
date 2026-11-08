# Connected Services — 0.8.33

HOME → Connected Services lists **Suno, fal, BUZZ, Modem** in that order. Static provider catalogue entries are never proof of live connection or account credits. Always preserve the separately connected providers and the original four HOME choices.

Suno and fal have TWO simple creator actions each: **Prepare Music Brief / Open Suno** and **Prepare Motion Brief / Open fal**. A brief uses the existing PlotPickle story evidence and enters an ordinary chat workflow without spending provider credits. **Open Suno** opens `https://suno.com/` and **Open fal** opens `https://fal.ai/dashboard` directly in the host browser through a URL-opening action. These two Open actions must not invoke a chat conversation or tool that writes the story. The actual login, account, pricing and purchases occur on the provider's own website, not inside PlotPickle. No usernames or passwords are collected or stored by PlotPickle.

A direct external link need not be preceded by a connection-status check. When users explicitly ask for provider status or credits, use live authorized provider tools and distinguish **Not verified**, **Connected / Ready for authorized job**, **Connected / Billing blocked**, and **Provider unavailable**. Do not invent account statuses or session identity.

For fal video production, require a verified saved source image, eligible model, input contract, supported native duration, current job cost and explicit creator approval before a paid submission. A 3–15 second PlotPickle Motion Span is editorial timing, not a statement that every fal model offers those durations. A fal media URL is not a verified or archived project asset. Import only retrievable decoded bytes with source binding, SHA-256, actual frame rate/duration and author review; see `../../plotpickle-fal-production/SKILL.md`.

Suno uses its own plan credits and authorization. BUZZ invitation-only HOME/CHAT/ELARA/SHOW is not verified deployed. Modem remains planned. A static catalogue is never proof another plugin is installed. No provider password, API token, payment card or secret belongs in chat, plugin files or a PPF.
