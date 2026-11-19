# Audio Summary

Turn a recording into one tidy document, run by Claude.

Give Claude an interview, a call, a meeting or a voice note, and you get back
one document with:

- **About this recording**: who, what, when, how long, and how reliable the
  transcript is
- **Summary**: key points by topic, next steps and deadlines exactly as said
  (with timestamps), and open questions
- **Full transcript**: cleaned up, speaker-labelled and timestamped, in one
  continuous section, translated into your language if people spoke another

Transcription runs locally with Whisper (small, int8) through
[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx): no API key, no GPU, and
the audio isn't uploaded anywhere. Anything Claude can't make out is marked
`[unclear]` rather than guessed.

## Examples

Once installed, give Claude a file and ask:

- *"Summarise this recording."*
- *"Turn this interview into a transcript with a summary."*
- *"Here's a voice note in German, what does it say?"*
- *"Write up the minutes from this call, with next steps."*

## What you need

- Claude with a shell: **Claude Code**, or the **Claude app** with code
  execution (or a linked computer)
- **Python 3**
- **ffmpeg**, or on macOS the built-in `afconvert` (enough for .m4a, .mp3,
  .wav; install ffmpeg for .opus and .ogg voice notes)
- About 375 MB of disk for the model, downloaded once (about 1 GB) to
  `~/.cache/audio-summary`
- Optional: a **Claude Docs** connector. Without one, the result is a
  Markdown file next to the recording.

Speed: roughly 4x real time on 2 CPU cores, faster on more. A 30-minute call
takes about 7 to 8 minutes on 2 cores.

## Install

**Claude app**: open **Customize → Plugins**, click **Add → Add marketplace →
Add from a repository**, enter `phillippmueller/audio-summary`, and install
**Audio Summary**.

**Claude Code**:

```
/plugin marketplace add phillippmueller/audio-summary
/plugin install audio-summary@audio-summary
```

## What it will and won't do

- **Never guesses** names, numbers or words it can't hear: they become
  `[unclear]` or `[unclear: best guess]`.
- **Summarises only what was said**: no advice or evaluation unless you ask.
- **Doesn't upload** the audio or transcript anywhere but the document you
  asked for.
- **Never deletes** your recording.
- Speaker labels are inferred from context and timestamps are approximate
  (about 25 seconds). Dialects such as Swiss German come out rougher.

## Files

```
plugins/audio-summary/skills/audio-summary/
  SKILL.md                 the workflow, step by step
  scripts/transcribe.py    local Whisper transcription in 25-second chunks
```

## License

MIT. See [LICENSE](LICENSE) and [PRIVACY.md](PRIVACY.md).
