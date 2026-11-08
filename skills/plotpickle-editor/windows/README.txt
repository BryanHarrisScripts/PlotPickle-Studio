PLOTPICKLE CREATIVE EDITOR - WINDOWS STARTER (Phase 1 + Audio MVP, v0.8.31)

QUICK START
1. Extract this ZIP to a writable folder, such as Desktop\PlotPickle-Editor.
2. Install Python 3.11 or newer (64-bit) and FFmpeg with ffprobe on PATH.
   In Command Prompt, run: py -0p      (lists installed Python versions)
   In Command Prompt, run: ffmpeg -version
3. Double-click Start-PlotPickle-Editor.cmd. The launcher selects Python 3.11+.
   The browser opens: http://127.0.0.1:8765
4. Click Import fal Shot 01 to download the ALREADY generated video.
   This does not submit a new paid generation.
5. Edit the timeline and click Render Draft for a frame-verified 24fps MP4.

DATA LOCATION (unchanged)
Default: %LOCALAPPDATA%\PlotPickle\Projects\The Third Bell\Editor
This avoids assuming C:\Users\<name>\Videos actually exists. Windows may redirect Videos.
Existing old drafts at %USERPROFILE%\Videos\PlotPickle\The Third Bell\Editor
are reused automatically if they contain editor-draft.json.

To use a different local drive such as G:, before launching set a user environment
variable named PLOTPICKLE_EDITOR_ROOT to a writable full path, e.g.
G:\PlotPickle-Media\The Third Bell\Editor
You may also edit the DATA_ROOT setting in the .cmd file.

TROUBLESHOOTING
- Python 3.8 traceback: the old launcher ran 'py -3' and selected Python 3.8.
  This build detects Python 3.11+ and fails with a clear message if not found.
- FileNotFoundError for C:\Users\...\Videos: the old starter assumed a missing
  Videos directory; this build uses LocalAppData instead.
- FFmpeg missing: install FFmpeg and add ffmpeg.exe and ffprobe.exe to PATH.
- Port 8765 in use: close the previous editor instance before restarting.

SECURITY AND SCOPE
This is a functional LOCAL editor prototype at localhost. Do not expose port
8765 to the internet. No secure ChatGPT-to-Windows control bridge is connected.
Only one video clip can be rendered; dialogue, Foley, ambience and music WAV sources
can now be mixed independently. Lip sync is still not implemented.
Your native PlotPickle PPF is not changed by this editor.

PLAYBACK BRIDGE REPAIR (v0.8.30)
- Fixes the browser error: "Cannot read properties of undefined (reading 'split')".
- The browser now uses a same-origin /media/... preview URL issued by the local
  service. Windows paths and provider URLs remain private in the API.
- Existing imported Shot 01 media, draft edits and history are preserved.
- You must close the previous running editor (Ctrl+C in its CMD window) before
  replacing the extracted application files and restarting.
- When Shot 01 was already imported, it plays immediately without re-import.
- If it was not imported, use Import fal Shot 01 once; this uses the completed
  video, not a new paid generation.
- If the editor still shows an error, force-refresh the page (Ctrl+F5) and
  verify there is only one editor server running on port 8765.

AUDIO EDITOR (v0.8.31)
- The existing Ocean hush and Distant gulls cues now have local, generated demo WAVs.
  These are TEMPORARY SYNTHETIC SOUND DESIGN REFERENCES, NOT FIELD RECORDINGS.
  No fal credits or remote sound service is used to create them.
- Select an audio cue (Dialogue/Foley/Ambience/Music) in the Timeline.
  You can edit Start Frame, Duration (24 fps), Gain dB, Mute, and notes.
- To use your own recording, click the cue, choose a WAV file, then Attach WAV.
  The editor stores an immutable 48 kHz stereo normalized copy in the LOCAL audio vault.
  Upload limit: 32 MiB; one WAV is at most 5 minutes. The source screenplay is untouched.
- Click Render Picture + Sound to mix every unmuted cue with an attached WAV,
  accurately scheduled to the 24 fps timeline (2000 audio samples per frame).
- When verification finishes, the video player changes to the mixed 1080p/24fps
  draft. Click Download Mix to keep that exact render. Undo/edit creates another
  revision and never rewrites the prior render.
- If you add an audio cue without attaching a WAV, it is a marker only. The
  render receipt lists those skipped cues; it will not invent missing audio.
- This phase does NOT synthesize speech, lip-sync characters, add multishot
  transitions, or turn the local editor into a ChatGPT-hosted frontend.
- Files and history continue in the same PLOTPICKLE_EDITOR_ROOT location.
- To update, stop the existing editor with Ctrl+C, extract ZIP over the same
  application folder, launch, and hard-refresh the browser (Ctrl+F5).

SECURITY NOTES
Only the current local browser origin may POST edits or WAV attachments.
WAV files are independently checked, converted, stored and hashed inside the
local media root. The server does not expose arbitrary Windows paths, bind a
public port, enable cloud access, or connect the legacy Factory tunnel.
