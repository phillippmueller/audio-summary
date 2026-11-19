"""Transcribe a recording locally with Whisper (small, int8) via sherpa-onnx.

Usage:
    python3 -I transcribe.py <audio_file> <work_dir> [--chunk 25] [--language de] [--models DIR]

Writes <work_dir>/transcript.txt: one line per chunk, "[mm:ss] text", flushed as
it goes so progress can be read while it runs. Prints "i/n" per chunk.

Audio is converted to 16 kHz mono WAV with ffmpeg, or with macOS's built-in
afconvert when ffmpeg is missing. Nothing leaves the machine.
"""
import argparse
import os
import shutil
import subprocess
import sys
import wave

import numpy as np
import sherpa_onnx

RATE = 16000
DEFAULT_MODELS = os.environ.get(
    "AUDIO_SUMMARY_MODELS", os.path.expanduser("~/.cache/audio-summary/models"))


def to_wav(audio, out):
    if shutil.which("ffmpeg"):
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", audio,
               "-ar", str(RATE), "-ac", "1", "-c:a", "pcm_s16le", out]
    elif shutil.which("afconvert"):
        cmd = ["afconvert", "-f", "WAVE", "-d", f"LEI16@{RATE}", "-c", "1", audio, out]
    else:
        sys.exit("Need ffmpeg (or afconvert on macOS) to read the audio file.")
    subprocess.run(cmd, check=True)


def read_wav(path):
    with wave.open(path) as w:
        if w.getframerate() != RATE or w.getnchannels() != 1 or w.getsampwidth() != 2:
            sys.exit(f"Unexpected WAV format in {path}")
        data = w.readframes(w.getnframes())
    return np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audio")
    p.add_argument("work")
    p.add_argument("--chunk", type=int, default=25, help="seconds per chunk (Whisper max is 30)")
    p.add_argument("--language", default="", help="e.g. en, de; empty = auto-detect per chunk")
    p.add_argument("--models", default=DEFAULT_MODELS)
    a = p.parse_args()

    md = os.path.join(a.models, "sherpa-onnx-whisper-small")
    if not os.path.isdir(md):
        sys.exit(f"Model not found in {md}. See the setup step in SKILL.md.")
    os.makedirs(a.work, exist_ok=True)
    wav = os.path.join(a.work, "audio-16k.wav")
    to_wav(a.audio, wav)
    samples = read_wav(wav)

    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=os.path.join(md, "small-encoder.int8.onnx"),
        decoder=os.path.join(md, "small-decoder.int8.onnx"),
        tokens=os.path.join(md, "small-tokens.txt"),
        language=a.language, task="transcribe",
        num_threads=os.cpu_count() or 2, tail_paddings=500)

    step = a.chunk * RATE
    n = (len(samples) + step - 1) // step
    with open(os.path.join(a.work, "transcript.txt"), "w") as out:
        for i in range(n):
            piece = samples[i * step:(i + 1) * step]
            if len(piece) >= RATE // 2:  # sub-0.5 s tails can crash the decoder
                s = rec.create_stream()
                s.accept_waveform(RATE, piece)
                rec.decode_stream(s)
                t = i * a.chunk
                out.write(f"[{t // 60:02d}:{t % 60:02d}] {s.result.text.strip()}\n")
                out.flush()
            print(f"{i + 1}/{n}", flush=True)
    os.remove(wav)


if __name__ == "__main__":
    main()
