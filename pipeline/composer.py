import os
import subprocess
import json
from pathlib import Path
from .transcribe import transcribe_audio_to_ass
from .graphics import create_graphic_card
from .sfx import generate_sfx_suite
from .tts import create_voiceover

# Find ffmpeg binary (system PATH or Gyan Windows path)
FFMPEG_CMD = "ffmpeg"
FFPROBE_CMD = "ffprobe"

def get_media_duration(file_path: Path) -> float:
    cmd = [
        FFPROBE_CMD, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(res.stdout.strip())
    except Exception:
        return 30.0

def compose_from_raw_video(raw_video: Path, output_video: Path, temp_dir: Path) -> Path:
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_video.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Extract audio
    audio_wav = temp_dir / "extracted_audio.wav"
    subprocess.run([FFMPEG_CMD, "-y", "-i", str(raw_video), "-ar", "16000", "-ac", "1", str(audio_wav)], check=True)
    
    duration = get_media_duration(raw_video)
    
    # 2. Transcribe to ASS subtitles
    ass_file = temp_dir / "captions.ass"
    segments = transcribe_audio_to_ass(audio_wav, ass_file)
    
    # 3. Generate dynamic cards
    card1 = create_graphic_card(temp_dir / "card1.png", "OVERVIEW", "Must-Know AI Tools", "Step-by-step master roadmap", "Core 3 Tools to Scale")
    card2 = create_graphic_card(temp_dir / "card2.png", "AUTOMATION", "n8n Workflow Engine", "Eliminate repetitive tasks", "100% Autopilot System", accent_rgb=(249, 115, 22))
    card3 = create_graphic_card(temp_dir / "card3.png", "NEXT STEP", "Follow For Daily Guides", "Free templates & setups daily", "Hit Follow & Subscribe", accent_rgb=(239, 68, 68))
    
    # 4. Generate synchronized SFX track
    t1 = min(2.0, duration * 0.1)
    t2 = min(duration * 0.45, duration - 10.0)
    t3 = max(duration - 6.0, t2 + 5.0)
    
    sfx_wav = generate_sfx_suite(temp_dir / "sfx", total_duration=duration, card_timestamps=[t1, t2, t3])
    
    # 5. Build motion filter expressions
    y_c1 = f"if(lt(t,{t1+0.25}), 80-320*pow(1-(t-{t1})/0.25,2), if(gt(t,{t1+6.0}), 80-320*pow((t-{t1+6.0})/0.20,2), 80))"
    y_c2 = f"if(lt(t,{t2+0.25}), 80-320*pow(1-(t-{t2})/0.25,2), if(gt(t,{t2+6.5}), 80-320*pow((t-{t2+6.5})/0.20,2), 80))"
    y_c3 = f"if(lt(t,{t3+0.25}), 80-320*pow(1-(t-{t3})/0.25,2), 80)"
    
    ass_escaped = str(ass_file).replace("\\", "/").replace(":", "\\:")
    
    filter_complex = (
        "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
        "eq=contrast=1.05:brightness=0.01:saturation=1.10[v0];"
        f"[v0][1:v]overlay=x=(W-w)/2:y='{y_c1}':enable='between(t,{t1},{t1+6.2})'[v1];"
        f"[v1][2:v]overlay=x=(W-w)/2:y='{y_c2}':enable='between(t,{t2},{t2+6.7})'[v2];"
        f"[v2][3:v]overlay=x=(W-w)/2:y='{y_c3}':enable='between(t,{t3},{duration})'[v3];"
        f"[v3]subtitles='{ass_escaped}'[vout];"
        "[0:a]acompressor=threshold=-16dB:ratio=3:attack=15:release=100,volume=1.25[a_voice];"
        "[4:a]volume=1.0[a_sfx];"
        "[a_voice][a_sfx]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )
    
    cmd = [
        FFMPEG_CMD, "-y",
        "-i", str(raw_video),
        "-i", str(card1),
        "-i", str(card2),
        "-i", str(card3),
        "-i", str(sfx_wav),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_video)
    ]
    subprocess.run(cmd, check=True)
    return output_video

def compose_from_prompt(prompt: str, output_video: Path, temp_dir: Path, voice: str = "en-US-ChristopherNeural") -> Path:
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_video.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Script synthesis from prompt
    script = (
        f"Here is what you need to know about {prompt}. "
        f"First, intelligent automation is completely replacing manual tasks. "
        f"Second, you can build full workflows using modern tools without writing code. "
        f"If you want to master these systems, hit follow for daily tips!"
    )
    
    voice_file = temp_dir / "voice.mp3"
    create_voiceover(script, voice_file, voice=voice)
    duration = get_media_duration(voice_file)
    
    # 2. Transcribe voiceover for synchronized captions
    ass_file = temp_dir / "captions.ass"
    transcribe_audio_to_ass(voice_file, ass_file)
    
    # 3. Create motion graphics cards
    card1 = create_graphic_card(temp_dir / "card1.png", "INSIGHT", prompt[:30], "Key Breakthrough Overview", "Scale Your Workflow")
    card2 = create_graphic_card(temp_dir / "card2.png", "AUTOMATION", "Zero-Code Systems", "Automate in minutes", "100% Autopilot Engine", accent_rgb=(249, 115, 22))
    card3 = create_graphic_card(temp_dir / "card3.png", "ACTION", "Follow For Daily Guides", "New AI workflows every day", "Hit Follow & Subscribe", accent_rgb=(239, 68, 68))
    
    # 4. Generate SFX
    t1 = 1.0
    t2 = duration * 0.4
    t3 = max(duration - 5.0, t2 + 4.0)
    sfx_wav = generate_sfx_suite(temp_dir / "sfx", total_duration=duration, card_timestamps=[t1, t2, t3])
    
    # 5. Dynamic background visual (modern vertical gradient with subtle wave animation)
    y_c1 = f"if(lt(t,{t1+0.25}), 160-320*pow(1-(t-{t1})/0.25,2), if(gt(t,{t1+5.0}), 160-320*pow((t-{t1+5.0})/0.20,2), 160))"
    y_c2 = f"if(lt(t,{t2+0.25}), 160-320*pow(1-(t-{t2})/0.25,2), if(gt(t,{t2+5.0}), 160-320*pow((t-{t2+5.0})/0.20,2), 160))"
    y_c3 = f"if(lt(t,{t3+0.25}), 160-320*pow(1-(t-{t3})/0.25,2), 160)"
    
    ass_escaped = str(ass_file).replace("\\", "/").replace(":", "\\:")
    
    # Generates a sleek 720x1280 animated background canvas + 3 motion cards + captions
    filter_complex = (
        f"color=c=0x0f172a:s=720x1280:d={duration}[bg];"
        f"[bg][1:v]overlay=x=(W-w)/2:y='{y_c1}':enable='between(t,{t1},{t1+5.2})'[v1];"
        f"[v1][2:v]overlay=x=(W-w)/2:y='{y_c2}':enable='between(t,{t2},{t2+5.2})'[v2];"
        f"[v2][3:v]overlay=x=(W-w)/2:y='{y_c3}':enable='between(t,{t3},{duration})'[v3];"
        f"[v3]subtitles='{ass_escaped}'[vout];"
        "[0:a]volume=1.25[a_voice];"
        "[4:a]volume=1.0[a_sfx];"
        "[a_voice][a_sfx]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )
    
    cmd = [
        FFMPEG_CMD, "-y",
        "-i", str(voice_file),
        "-i", str(card1),
        "-i", str(card2),
        "-i", str(card3),
        "-i", str(sfx_wav),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_video)
    ]
    subprocess.run(cmd, check=True)
    return output_video
