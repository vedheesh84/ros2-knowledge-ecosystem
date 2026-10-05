#!/usr/bin/env python3
"""Agentic podcast -> many Instagram reel clips."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from make_reel import normalize_source, probe_duration, transcribe_source, write_ass  # noqa: E402
from reel_style import crop_filter, styled_line  # noqa: E402
from video_fetch_server import build_instagram_caption  # noqa: E402

MIN_CLIP_SEC = 12.0
MAX_CLIP_SEC = 90.0
IDEAL_CLIP_SEC = 35.0
MIN_WORDS = 4


def ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def write_ass_for_clip(segments: list[dict], clip_start: float, clip_end: float, ass_path: Path) -> None:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Reel,Arial Black,58,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,4,1,2,60,60,220,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for seg in segments:
        start = max(float(seg["start"]), clip_start)
        end = min(float(seg["end"]), clip_end)
        if end <= start:
            continue
        text = styled_line(seg.get("text", ""))
        if not text:
            continue
        rel_start = start - clip_start
        rel_end = end - clip_start
        lines.append(f"Dialogue: 0,{ts(rel_start)},{ts(rel_end)},Reel,,0,0,0,,{text}\n")
    ass_path.write_text("".join(lines), encoding="utf-8")


def plan_clips(segments: list[dict], total_duration: float) -> list[dict]:
    usable = [s for s in segments if s.get("text", "").strip()]
    if not usable:
        return []

    clips: list[dict] = []
    bucket: list[dict] = []
    bucket_start: float | None = None

    def flush(force: bool = False) -> None:
        nonlocal bucket, bucket_start
        if not bucket or bucket_start is None:
            bucket = []
            bucket_start = None
            return
        end = float(bucket[-1]["end"])
        duration = end - bucket_start
        words = len(" ".join(s["text"] for s in bucket).split())
        if not force and duration < MIN_CLIP_SEC:
            return
        if duration < 5 or words < MIN_WORDS:
            bucket = []
            bucket_start = None
            return
        clips.append(
            {
                "start": round(bucket_start, 2),
                "end": round(min(end, bucket_start + MAX_CLIP_SEC), 2),
                "segments": list(bucket),
                "text": " ".join(s["text"] for s in bucket).strip(),
                "duration": round(min(end, bucket_start + MAX_CLIP_SEC) - bucket_start, 2),
            }
        )
        bucket = []
        bucket_start = None

    for seg in usable:
        if not bucket:
            bucket_start = float(seg["start"])
        bucket.append(seg)
        duration = float(seg["end"]) - float(bucket_start)
        word_count = len(" ".join(s["text"] for s in bucket).split())

        if duration >= MAX_CLIP_SEC:
            flush(force=True)
            continue
        if duration >= IDEAL_CLIP_SEC and word_count >= MIN_WORDS:
            flush(force=True)
            continue
        if duration >= MIN_CLIP_SEC and word_count >= MIN_WORDS + 4:
            flush(force=True)

    flush(force=True)

    # Fill long silent tail with one final chunk if substantial speech remains
    if not clips and usable:
        start = float(usable[0]["start"])
        end = min(float(usable[-1]["end"]), start + MAX_CLIP_SEC)
        clips.append(
            {
                "start": round(start, 2),
                "end": round(end, 2),
                "segments": usable,
                "text": " ".join(s["text"] for s in usable).strip(),
                "duration": round(end - start, 2),
            }
        )

    # De-duplicate overlapping plans
    cleaned: list[dict] = []
    last_end = -1.0
    for clip in clips:
        if clip["start"] < last_end - 1:
            continue
        cleaned.append(clip)
        last_end = clip["end"]

    if not cleaned and total_duration > MIN_CLIP_SEC:
        cleaned.append(
            {
                "start": 0.0,
                "end": round(min(total_duration, MAX_CLIP_SEC), 2),
                "segments": usable[:8],
                "text": " ".join(s["text"] for s in usable[:8]).strip(),
                "duration": round(min(total_duration, MAX_CLIP_SEC), 2),
            }
        )
    return cleaned


def render_clip(
    source: Path,
    normalized: Path,
    output: Path,
    clip: dict,
    camera: str,
    ass_path: Path,
) -> None:
    duration = clip["end"] - clip["start"]
    ass_escaped = str(ass_path).replace(":", r"\:").replace("'", r"\'")
    vf = f"{crop_filter(camera)},ass='{ass_escaped}'"
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{clip['start']:.3f}",
        "-i",
        str(normalized),
        "-ss",
        f"{clip['start']:.3f}",
        "-i",
        str(source),
        "-t",
        f"{duration:.3f}",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0?",
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:max_len] or "clip").strip("-")


def run_agent(
    source: Path,
    output_dir: Path,
    camera: str = "right",
    max_clips: int | None = None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    duration = probe_duration(source)
    print(f"Source: {source}")
    print(f"Duration: {duration:.1f}s")

    print("Transcribing full podcast...")
    transcript = transcribe_source(source, 0.0, duration)
    segments = transcript.get("segments", [])
    print(f"Speech segments: {len(segments)} ({transcript.get('engine', 'unknown')})")

    clips = plan_clips(segments, duration)
    if max_clips:
        clips = clips[:max_clips]
    print(f"Planned clips: {len(clips)}")

    manifest = {
        "source": str(source),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "duration_sec": round(duration, 2),
        "engine": transcript.get("engine"),
        "clip_count": len(clips),
        "clips": [],
    }

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        print("Normalizing video once...")
        normalized = normalize_source(source, 0.0, duration, tmp_dir)

        for index, clip in enumerate(clips, start=1):
            title = slugify(clip["text"][:60])
            base = f"clip-{index:02d}-{title}"
            mp4_path = output_dir / f"{base}.mp4"
            caption_path = output_dir / f"{base}.caption.txt"
            ass_path = tmp_dir / f"{index}.ass"

            write_ass_for_clip(clip["segments"], clip["start"], clip["end"], ass_path)
            print(f"[{index}/{len(clips)}] Rendering {clip['start']:.1f}s-{clip['end']:.1f}s -> {mp4_path.name}")
            render_clip(source, normalized, mp4_path, clip, camera, ass_path)

            caption = build_instagram_caption(clip["text"])
            caption_path.write_text(caption.get("caption", clip["text"]), encoding="utf-8")

            manifest["clips"].append(
                {
                    "index": index,
                    "file": mp4_path.name,
                    "caption_file": caption_path.name,
                    "start": clip["start"],
                    "end": clip["end"],
                    "duration": clip["duration"],
                    "text": clip["text"],
                    "instagram_caption": caption.get("caption", ""),
                }
            )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest -> {manifest_path}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic podcast clip generator")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=APP_DIR / "samples" / "podcast-clips")
    parser.add_argument("--camera", choices=["left", "right", "center"], default="right")
    parser.add_argument("--max-clips", type=int, default=None)
    args = parser.parse_args()
    if not args.source.exists():
        raise SystemExit(f"Source not found: {args.source}")
    run_agent(args.source, args.output_dir, args.camera, args.max_clips)


if __name__ == "__main__":
    main()
