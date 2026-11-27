# PlotPickle Studio

<p align="center">
  <img src="assets/studio-logo.png" alt="PlotPickle Studio" width="320">
</p>

**Your story. Your decisions. Your cut.**

**Personal ChatGPT plugin**

PlotPickle Studio is distributed for personal use through ChatGPT’s **Plugins → Personal** area. Public marketplace distribution and an open-source release of the current plugin are outside the project’s plans. This public GitHub repository provides documentation and release history. Previously published material carries the licence identified with that material.

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

## Developer architecture

PlotPickle separates its creative core from the infrastructure that runs it. The aim is portability through host-specific integrations, not dependence on a particular model or platform. The current implementation has limitations; other potential hosts remain untested.

The architecture includes two complementary feedback loops: the creator learns through visual experimentation, while PlotPickle can improve through reviewed research, open-source discovery (OSS Radar), optional feedback and tested releases. System improvements are proposals until reviewed and approved; private stories are not automatically collected for training or used to change the system.

<p align="center">
  <img src="assets/plotpickle-developer-architecture.svg" alt="PlotPickle developer architecture: creative core, host adapters, AI infrastructure, optional tools and two feedback loops for human learning and reviewed system evolution" width="100%">
</p>

## Install in ChatGPT

1. Sign in to [ChatGPT](https://chatgpt.com/) with the account you want to use.
2. Open **Plugins → Personal**. Under **Created by you**, select **PlotPickle Studio** if it is already listed.
3. Select **Install plugin** or the **+** button if shown. If prompted to connect to Studio, review the permissions and follow the ChatGPT sign-in prompts.
4. Start a conversation, type `@PlotPickle Studio`, select the plugin, and ask **Open Studio HOME**.

### Set up from a ZIP

If PlotPickle Studio is missing from **Personal**, use a current PlotPickle Studio plugin ZIP made available for personal setup. Check [GitHub Releases](https://github.com/BryanHarrisScripts/PlotPickle-Studio/releases) for a release explicitly marked for personal installation and compare the ZIP’s SHA-256 checksum with the one supplied for that version. The archived v2.0.55 ZIP points to a retired Studio connection.

In ChatGPT, open **Plugins → Add** and start **Plugin Creator** if offered. Install Plugin Creator if prompted, attach the ZIP in its conversation, and ask it to create PlotPickle Studio as a personal plugin. Once it appears under **Personal**, follow the steps above to install and connect it. Setup depends on your account’s plugin permissions and access to the Studio connection.

[OpenAI’s plugin installation and setup instructions](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt)

For release packaging and verification, see [RELEASES.md](RELEASES.md).

## Licensing

**[Open Technology](docs/licensing/OPEN-TECHNOLOGY.md)** — MIT for designated software.

**[Shared Creativity](docs/licensing/SHARED-CREATIVITY.md)** — CC BY-NC-SA 4.0 for designated creative and educational works.

The licence supplied with each published file or release governs that material. User stories remain under their creators’ chosen terms.

**The human remains the author.**
