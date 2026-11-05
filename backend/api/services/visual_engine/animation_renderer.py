"""
FORGE Animation Renderer
Generic topic-agnostic Manim renderer.

Reads a FORGE lesson JSON and renders a technical MP4.
No topic-specific branches are used.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCENE_TEMPLATE = r'''
from manim import *
import json

LESSON = __LESSON__


def point(p):
    p = p if isinstance(p, dict) else {}
    x = float(p.get("x", 50))
    y = float(p.get("y", 50))
    return ((x - 50) / 50 * 6, (50 - y) / 50 * 3.2, 0)


def color(style):
    style = style if isinstance(style, dict) else {}
    return {
        "input": BLUE_C,
        "output": GREEN_C,
        "active": YELLOW_C,
        "warning": ORANGE,
        "error": RED_C,
    }.get(str(style.get("tone", "default")).lower(), BLUE_C)


def label(e):
    if e.get("label") is not None:
        return str(e["label"])
    data = e.get("data")
    if isinstance(data, list):
        return "   ".join(str(x) for x in data)
    return str(data if data is not None else e.get("id", ""))


class FORGEVisualLesson(Scene):
    def construct(self):
        self.camera.background_color = "#071018"
        self.objects = {}
        self.specs = {}
        self.scene_runtime = []

        title = Text(str(LESSON.get("title", LESSON.get("topic", "FORGE"))), font_size=38)
        self.play(FadeIn(title), run_time=.4)
        self.wait(.5)
        self.play(FadeOut(title), run_time=.25)

        for scene in LESSON.get("scenes", []):
            if isinstance(scene, dict):
                self.render_scene(scene)

    def make(self, e):
        t = str(e.get("type", "text")).lower()
        c = color(e.get("style"))
        txt = label(e)

        if t in {"text", "label"}:
            obj = Text(txt, font_size=28, color=c)
        elif t == "equation":
            try:
                obj = MathTex(txt, font_size=32, color=c)
            except Exception:
                obj = Text(txt, font_size=25, color=c)
        elif t == "code":
            try:
                obj = Code(code=txt, language="Python", font="Monospace", background="window", font_size=18)
            except Exception:
                obj = Text(txt, font_size=22, color=c)
        elif t == "circle":
            obj = Circle(radius=.55, color=c, stroke_width=3)
        elif t == "node":
            body = Circle(radius=.38, color=c, stroke_width=3, fill_opacity=.15)
            caption = Text(txt, font_size=20).next_to(body, DOWN, buff=.12)
            obj = VGroup(body, caption)
        elif t == "pointer":
            arrow = Arrow(UP*.55, ORIGIN, buff=0, color=c, stroke_width=4)
            caption = Text(txt, font_size=20).next_to(arrow, UP, buff=.05)
            obj = VGroup(arrow, caption)
        elif t == "array":
            values = e.get("data")
            values = values if isinstance(values, list) else [txt]
            cells = []
            for value in values:
                sq = Square(.72, color=c, stroke_width=2)
                value_text = Text(str(value), font_size=21).move_to(sq)
                cells.append(VGroup(sq, value_text))
            row = VGroup(*cells).arrange(RIGHT, buff=.04)
            if e.get("label"):
                heading = Text(str(e["label"]), font_size=21).next_to(row, UP, buff=.15)
                obj = VGroup(heading, row)
            else:
                obj = row
        elif t == "matrix":
            rows = []
            data = e.get("data")
            if isinstance(data, list):
                for row_data in data:
                    row_data = row_data if isinstance(row_data, list) else [row_data]
                    cells = []
                    for value in row_data:
                        sq = Square(.55, color=c, stroke_width=2)
                        value_text = Text(str(value), font_size=18).move_to(sq)
                        cells.append(VGroup(sq, value_text))
                    rows.append(VGroup(*cells).arrange(RIGHT, buff=.03))
                obj = VGroup(*rows).arrange(DOWN, buff=.03)
            else:
                obj = Text(txt, font_size=22, color=c)
        elif t == "table":
            data = e.get("data")
            lines = []
            if isinstance(data, list):
                for row in data[:8]:
                    lines.append(" | ".join(str(v) for v in row[:8]) if isinstance(row, list) else str(row))
            obj = Text("\n".join(lines) or txt, font_size=20, color=c)
        else:
            # Generic visual container for graph/tree/layer/packet/database/etc.
            box = RoundedRectangle(width=2.0, height=1.05, corner_radius=.12, color=c, stroke_width=3, fill_opacity=.10)
            caption = Text(txt, font_size=20).move_to(box)
            obj = VGroup(box, caption)

        obj.move_to(point(e.get("position")))
        return obj

    def connection(self, e):
        source = self.objects.get(e.get("from") or e.get("source"))
        target = self.objects.get(e.get("to") or e.get("target"))
        if source is None or target is None:
            return None
        return Arrow(source.get_center(), target.get_center(), buff=.25, color=color(e.get("style")), stroke_width=3)

    def action(self, a):
        name = str(a.get("action", "wait")).lower()
        target_id = a.get("target")
        target = self.objects.get(target_id)
        try:
            duration = float(a.get("duration", .7))
        except (TypeError, ValueError):
            duration = .7
        duration = max(.05, min(duration, 4))

        if name == "wait":
            self.wait(duration)
        elif name in {"highlight", "compare", "trace"}:
            targets = a.get("value") if isinstance(a.get("value"), list) else [target_id]
            animations = [Indicate(self.objects[x], color=YELLOW_C) for x in targets if x in self.objects]
            if animations:
                self.play(*animations, run_time=duration)
        elif name in {"remove", "fade"} and target is not None:
            self.play(FadeOut(target), run_time=duration)
        elif name == "move" and target is not None:
            self.play(target.animate.move_to(point(a.get("value"))), run_time=duration)
        elif name == "create" and isinstance(a.get("value"), dict):
            spec = dict(a["value"])
            spec.setdefault("id", target_id or f"generated_{len(self.objects)}")
            obj = self.make(spec)
            self.objects[spec["id"]] = obj
            self.specs[spec["id"]] = spec
            self.play(FadeIn(obj), run_time=duration)
        elif name in {"replace", "update", "transform"} and target is not None and isinstance(a.get("value"), dict):
            spec = dict(self.specs.get(target_id, {}))
            spec.update(a["value"])
            spec["id"] = target_id
            replacement = self.make(spec)
            self.play(ReplacementTransform(target, replacement), run_time=duration)
            self.objects[target_id] = replacement
            self.specs[target_id] = spec
        elif name == "split" and target is not None:
            self.play(target.animate.scale(.65), run_time=duration)
        elif name == "merge" and target is not None:
            self.play(target.animate.scale(1.25), run_time=duration)
        else:
            self.wait(duration)

    def _safe_layout(self, objects, specs):
        """Keep generated visuals readable even when the planner gives poor coordinates."""
        if not objects:
            return

        # Fit oversized compound visuals to the safe frame.
        for obj in objects.values():
            try:
                if obj.width > 10.6:
                    obj.scale_to_fit_width(10.2)
                if obj.height > 5.0:
                    obj.scale_to_fit_height(4.6)
            except Exception:
                pass

        # Arrays/matrices/tables are primary teaching objects: center them and
        # give them their own horizontal band instead of allowing labels to pile up.
        primary = []
        for eid, obj in objects.items():
            t = str(specs.get(eid, {}).get("type", "")).lower()
            if t in {"array", "matrix", "table", "graph", "tree"}:
                primary.append((eid, obj, t))

        if primary:
            for idx, (_, obj, t) in enumerate(primary):
                if len(primary) == 1:
                    y = -0.05
                else:
                    y = 0.9 - idx * 1.7
                try:
                    obj.move_to([0, y, 0])
                except Exception:
                    pass

        # Text/equation/label/pointer elements are placed in clear lanes.
        lane_types = {"text", "label", "equation", "pointer", "circle"}
        lanes = []
        for eid, obj in objects.items():
            t = str(specs.get(eid, {}).get("type", "")).lower()
            if t in lane_types and not any(eid == x[0] for x in primary):
                lanes.append((eid, obj, t))
        for idx, (_, obj, _) in enumerate(lanes):
            if idx >= 5:
                break
            y = 2.05 - idx * 0.85
            try:
                obj.move_to([0, y, 0])
            except Exception:
                pass

        # Final collision pass: if two generated objects still intersect,
        # nudge the later object downward rather than rendering unreadable text.
        items = list(objects.items())
        for i in range(len(items)):
            _, a = items[i]
            for j in range(i + 1, len(items)):
                _, b = items[j]
                try:
                    if a.get_right()[0] > b.get_left()[0] and b.get_right()[0] > a.get_left()[0] and \
                       a.get_top()[1] > b.get_bottom()[1] and b.get_top()[1] > a.get_bottom()[1]:
                        b.shift(DOWN * min(0.75, max(0.35, a.height * 0.35)))
                except Exception:
                    pass

    def _scene_duration(self, scene):
        """Return a bounded, student-friendly total duration for one scene."""
        try:
            requested = float(scene.get("duration", 8.0))
        except (TypeError, ValueError):
            requested = 8.0
        return max(6.0, min(requested, 14.0))

    def render_scene(self, scene):
        scene_start = getattr(self.renderer, "time", 0.0)
        heading = Text(str(scene.get("title", "")), font_size=28, color=WHITE)
        heading.to_edge(UP, buff=.25)
        self.play(FadeIn(heading), run_time=.25)

        elements = scene.get("elements", [])
        if not isinstance(elements, list):
            elements = []

        for e in elements:
            if not isinstance(e, dict):
                continue
            eid = e.get("id") or f"element_{len(self.objects)}"
            e["id"] = eid
            self.specs[eid] = e
            if str(e.get("type", "")).lower() in {"arrow", "edge"}:
                continue
            try:
                obj = self.make(e)
                self.objects[eid] = obj
                self.play(FadeIn(obj), run_time=.16)
            except Exception:
                pass

        # Repair planner collisions before showing the complete scene.
        self._safe_layout(self.objects, self.specs)

        for e in elements:
            if not isinstance(e, dict) or str(e.get("type", "")).lower() not in {"arrow", "edge"}:
                continue
            try:
                obj = self.connection(e)
                if obj is not None:
                    eid = e.get("id") or f"connection_{len(self.objects)}"
                    self.objects[eid] = obj
                    self.play(Create(obj), run_time=.16)
            except Exception:
                pass

        for action in scene.get("actions", []):
            if isinstance(action, dict):
                self.action(action)

        narration = scene.get("narration", "")
        if isinstance(narration, dict):
            narration = narration.get("text", "")
        subtitle = None
        if narration:
            # Keep a short caption as a visual aid; full narration is also muxed
            # into the MP4 audio track by render_lesson().
            caption = str(narration).strip().replace("\n", " ")
            subtitle = Text(caption[:150], font_size=15, color=GREY_A)
            subtitle.to_edge(DOWN, buff=.28)
            self.play(FadeIn(subtitle), run_time=.15)

        target_duration = self._scene_duration(scene)
        elapsed = max(0.0, getattr(self.renderer, "time", 0.0) - scene_start)
        remaining = max(0.5, target_duration - elapsed)
        self.wait(remaining)

        if self.objects:
            self.play(*[FadeOut(o) for o in self.objects.values()], run_time=.22)
        if subtitle is not None and subtitle in self.mobjects:
            self.play(FadeOut(subtitle), run_time=.12)
        self.play(FadeOut(heading), run_time=.15)
        self.objects.clear()
        self.specs.clear()


if __name__ == "__main__":
    scene = FORGEVisualLesson()
'''



def _scene_narration(scene):
    narration = scene.get("narration", "") if isinstance(scene, dict) else ""
    if isinstance(narration, dict):
        narration = narration.get("text", "")
    return str(narration or "").strip()


def _synthesize_tts(text: str, output_path: Path) -> bool:
    """Generate a local narration track without requiring a cloud TTS service."""
    if not text.strip():
        return False
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)
        engine.save_to_file(text, str(output_path))
        engine.runAndWait()
        engine.stop()
        return output_path.exists() and output_path.stat().st_size > 1000
    except Exception as exc:
        print("[VOICE] pyttsx3 unavailable/failed:", exc)

    # Windows fallback: use the built-in System.Speech engine so the user does
    # not need a cloud TTS account. This is especially useful on a fresh FORGE
    # Windows setup where pyttsx3/pywin32 may not yet be installed.
    if sys.platform.startswith("win"):
        try:
            import base64
            import shutil
            ps = shutil.which("powershell.exe") or shutil.which("powershell")
            if ps:
                encoded_text = base64.b64encode(text.encode("utf-8")).decode("ascii")
                encoded_path = base64.b64encode(str(output_path).encode("utf-8")).decode("ascii")
                command = (
                    "Add-Type -AssemblyName System.Speech; "
                    f"$t=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded_text}')); "
                    f"$p=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded_path}')); "
                    "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    "$s.Rate=0; $s.Volume=100; $s.SetOutputToWaveFile($p); "
                    "$s.Speak($t); $s.Dispose();"
                )
                subprocess.run([ps, "-NoProfile", "-Command", command], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if output_path.exists() and output_path.stat().st_size > 1000:
                    return True
        except Exception as exc2:
            print("[VOICE] Windows System.Speech fallback failed:", exc2)

    return False


def _build_narration_audio(lesson: dict, tmp: Path, output_path: Path) -> bool:
    """Create one narration track aligned scene-by-scene with the rendered lesson."""
    scenes = lesson.get("scenes", []) if isinstance(lesson, dict) else []
    if not scenes or not any(_scene_narration(x) for x in scenes if isinstance(x, dict)):
        return False

    parts = []
    # Opening title timing in FORGEVisualLesson.
    opening = 1.15
    silent_open = tmp / "voice_open.wav"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=22050:cl=mono", "-t", str(opening), str(silent_open)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    parts.append(silent_open)

    for idx, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        target = max(6.0, min(float(scene.get("duration", 8.0) or 8.0), 14.0))
        narration = _scene_narration(scene)
        raw = tmp / f"voice_{idx:02d}.wav"
        padded = tmp / f"voice_part_{idx:02d}.wav"
        if narration and _synthesize_tts(narration, raw):
            # Start speaking shortly after the visual title/objects appear.
            delay_ms = 900
            duration = target + 0.49
            subprocess.run(["ffmpeg", "-y", "-i", str(raw), "-af", f"adelay={delay_ms}:all=1,apad", "-t", str(duration), str(padded)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            duration = target + 0.49
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", str(duration), str(padded)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        parts.append(padded)

    concat = tmp / "voice_concat.txt"
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c:a", "aac", "-b:a", "128k", str(output_path)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path.exists() and output_path.stat().st_size > 1000



def render_lesson(lesson: dict, output_path: str | Path) -> str:
    """Render a complete FORGE lesson to one MP4."""
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    source = SCENE_TEMPLATE.replace("__LESSON__", repr(lesson))

    with tempfile.TemporaryDirectory(prefix="forge_manim_") as tmp:
        tmp_path = Path(tmp)
        scene_file = tmp_path / "forge_generated_scene.py"
        scene_file.write_text(source, encoding="utf-8")

        media_dir = tmp_path / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable, "-m", "manim", "-qm",
            str(scene_file), "FORGEVisualLesson",
            "--media_dir", str(media_dir),
        ]
        print("FORGE Animation Renderer")
        print("Topic:", lesson.get("topic"))
        print("Scenes:", len(lesson.get("scenes", [])))
        subprocess.run(cmd, check=True)

        videos = list(media_dir.rglob("FORGEVisualLesson.mp4"))
        if not videos:
            raise FileNotFoundError("Manim finished but no MP4 was found.")

        source_video = max(videos, key=lambda p: p.stat().st_mtime)

        voice_path = tmp_path / "narration.m4a"
        has_voice = _build_narration_audio(lesson, tmp_path, voice_path)

        muxed_path = tmp_path / "final_faststart.mp4"
        cmd_mux = ["ffmpeg", "-y", "-i", str(source_video)]

        if has_voice:
            cmd_mux += [
                "-i", str(voice_path),
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest",
            ]
        else:
            cmd_mux += ["-c:v", "copy"]

        cmd_mux += ["-movflags", "+faststart", str(muxed_path)]
        subprocess.run(cmd_mux, check=True)

        output_path.write_bytes(muxed_path.read_bytes())
        print("VOICE_TRACK:", "enabled" if has_voice else "unavailable")
        print("FINAL_VIDEO:", output_path)

    return str(output_path)


def render_lesson_scene(
    lesson: dict,
    scene_index: int,
    output_path: str | Path,
) -> str:
    """Render one scene as an independent MP4 for progressive playback."""
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scenes = lesson.get("scenes", []) if isinstance(lesson, dict) else []
    if scene_index < 0 or scene_index >= len(scenes):
        raise IndexError(f"Scene index out of range: {scene_index}")

    scene_lesson = dict(lesson)
    scene_lesson["scenes"] = [scenes[scene_index]]

    return render_lesson(scene_lesson, output_path)

def main():
    parser = argparse.ArgumentParser(description="Render a FORGE visual lesson with Manim")
    parser.add_argument("--lesson", required=True, help="Path to lesson JSON")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    args = parser.parse_args()

    lesson_path = Path(args.lesson).resolve()
    output_path = Path(args.output).resolve()
    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))

    source = SCENE_TEMPLATE.replace("__LESSON__", repr(lesson))

    with tempfile.TemporaryDirectory(prefix="forge_manim_") as tmp:
        scene_file = Path(tmp) / "forge_generated_scene.py"
        scene_file.write_text(source, encoding="utf-8")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            "-m",
            "manim",
            "-qm",
            str(scene_file),
            "FORGEVisualLesson",
            "--media_dir",
            str(output_path.parent),
        ]
        print("FORGE Animation Renderer")
        print("Topic:", lesson.get("topic"))
        print("Scenes:", len(lesson.get("scenes", [])))
        subprocess.run(cmd, check=True)

        videos = list(output_path.parent.rglob("FORGEVisualLesson.mp4"))
        if not videos:
            raise FileNotFoundError("Manim finished but no MP4 was found.")

        source_video = max(videos, key=lambda p: p.stat().st_mtime)
        final_path = output_path if output_path.suffix.lower() == ".mp4" else output_path.with_suffix(".mp4")

        # Build narration locally and mux it into the MP4. The same ffmpeg pass
        # also moves the MP4 metadata to the front so browser playback can start
        # before the entire file has downloaded.
        voice_path = Path(tmp) / "narration.m4a"
        has_voice = _build_narration_audio(lesson, Path(tmp), voice_path)
        muxed_path = Path(tmp) / "final_faststart.mp4"
        cmd_mux = ["ffmpeg", "-y", "-i", str(source_video)]
        if has_voice:
            cmd_mux += ["-i", str(voice_path), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest"]
        else:
            cmd_mux += ["-c:v", "copy"]
        cmd_mux += ["-movflags", "+faststart", str(muxed_path)]
        subprocess.run(cmd_mux, check=True)
        final_path.write_bytes(muxed_path.read_bytes())
        print("VOICE_TRACK:", "enabled" if has_voice else "unavailable")
        print("FINAL_VIDEO:", final_path)


if __name__ == "__main__":
    main()
