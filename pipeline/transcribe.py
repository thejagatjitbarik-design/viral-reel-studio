import os
import whisper
from pathlib import Path
from typing import List, Dict

# Use "tiny" or "base" for speed and low-RAM Render cloud environments
MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
_model = None

def get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model(MODEL_NAME, device="cpu")
    return _model

def format_ass_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"

def transcribe_audio_to_ass(audio_path: Path, ass_output_path: Path, language: str = None) -> List[Dict]:
    model = get_whisper_model()
    kwargs = {"fp16": False}
    if language:
        kwargs["language"] = language
        
    result = model.transcribe(str(audio_path), **kwargs)
    segments = result.get("segments", [])
    
    ass_header = """[Script Info]
Title: Viral Reel Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ReelCaptions,Segoe UI,34,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,3,4,0,2,30,30,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Yellow highlight color code in ASS is &H0024D9FF&
    events = []
    for seg in segments:
        start_ts = format_ass_timestamp(seg["start"])
        end_ts = format_ass_timestamp(seg["end"])
        raw_text = seg["text"].strip()
        
        words = raw_text.split()
        if len(words) > 1:
            highlighted = words[0] + " {\\c&H0024D9FF&}" + " ".join(words[1:]) + "{\\c}"
        else:
            highlighted = "{\\c&H0024D9FF&}" + raw_text + "{\\c}"
            
        events.append(f"Dialogue: 0,{start_ts},{end_ts},ReelCaptions,,0,0,0,,{highlighted}")
        
    with open(ass_output_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")
        
    return segments
