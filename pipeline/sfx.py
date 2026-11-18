import numpy as np
import wave
from pathlib import Path

def write_wav(path: Path, data: np.ndarray, sample_rate=44100):
    data = np.clip(data, -1.0, 1.0)
    int_data = (data * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_data.tobytes())

def generate_sfx_suite(output_dir: Path, total_duration: float = 30.0, card_timestamps=None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    sr = 44100
    
    # 1. Whoosh
    t_w = np.linspace(0, 0.35, int(sr * 0.35), endpoint=False)
    whoosh = (0.6 * np.sin(2 * np.pi * (150 + 600 * (t_w / 0.35)) * t_w) + 0.4 * np.random.uniform(-1, 1, len(t_w))) * (np.sin(np.pi * (t_w / 0.35)) ** 2) * 0.85
    
    # 2. Bubble Pop
    t_p = np.linspace(0, 0.12, int(sr * 0.12), endpoint=False)
    pop = np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t_p * 35) + 150) / sr) * np.exp(-t_p * 30) * 0.9
    
    # 3. Crystal Ding
    t_d = np.linspace(0, 0.65, int(sr * 0.65), endpoint=False)
    ding = (0.6 * np.sin(2 * np.pi * 1046.50 * t_d) + 0.3 * np.sin(2 * np.pi * 1318.51 * t_d) + 0.2 * np.sin(2 * np.pi * 2093.00 * t_d)) * np.exp(-t_d * 6.5) * 0.8
    
    # 4. Combo whoosh + pop
    combo = np.zeros(int(sr * 0.5), dtype=np.float32)
    combo[:len(whoosh)] += whoosh * 0.7
    combo[int(0.18 * sr):int(0.18 * sr) + len(pop)] += pop * 0.85

    # Full track
    total_samples = int(sr * total_duration)
    sfx_track = np.zeros(total_samples, dtype=np.float32)
    
    if not card_timestamps:
        card_timestamps = [1.2, 8.0, 15.0, 22.0]
        
    for t_hit in card_timestamps:
        if t_hit < total_duration:
            start = int(t_hit * sr)
            end = min(start + len(combo), total_samples)
            sfx_track[start:end] += combo[:end - start] * 0.9
            
    # Subtle background lo-fi groove
    bg_chords = np.zeros(total_samples, dtype=np.float32)
    bar_len = int(sr * 2.666)
    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [130.81, 164.81, 196.0], [196.0, 246.94, 293.66]]
    
    for i in range(0, total_samples, bar_len):
        chord = chords[(i // bar_len) % len(chords)]
        seg_len = min(bar_len, total_samples - i)
        t_seg = np.linspace(0, seg_len / sr, seg_len, endpoint=False)
        env = np.exp(-t_seg * 0.7) * (1 - np.exp(-t_seg * 12))
        wave_sum = sum(np.sin(2 * np.pi * f * t_seg) for f in chord)
        bg_chords[i:i + seg_len] += wave_sum * env * 0.12
        
    final_mix = sfx_track * 0.85 + bg_chords * 0.05
    master_path = output_dir / "sfx_master.wav"
    write_wav(master_path, final_mix)
    return master_path
