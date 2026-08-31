import os
import math
import struct
import random
import wave

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

def generate_wav(filepath, samples, sample_rate=44100):
    """Generates a mono 16-bit PCM WAV file from float samples in [-1.0, 1.0]."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        packed_data = bytearray()
        for sample in samples:
            # Clamp sample to [-1.0, 1.0]
            sample = max(-1.0, min(1.0, sample))
            int_sample = int(sample * 32767)
            packed_data.extend(struct.pack('<h', int_sample))

        wav_file.writeframes(packed_data)

def generate_pistol_shot():
    """Suppressed pistol shot: short, quiet thud / pop."""
    sample_rate = 44100
    duration = 0.15
    num_samples = int(sample_rate * duration)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        # Envelope: very rapid attack, exponential decay
        env = math.exp(-35 * t)
        # Combination of low sine pop and filtered white noise
        freq = 150 - 80 * (i / num_samples)
        sine = math.sin(2 * math.pi * freq * t)
        noise = (random.random() * 2 - 1) * 0.4
        sample = (sine * 0.6 + noise * 0.4) * env
        samples.append(sample)

    return samples

def generate_rifle_shot():
    """Assault rifle shot: sharp, punchy gunshot burst."""
    sample_rate = 44100
    duration = 0.25
    num_samples = int(sample_rate * duration)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        env = math.exp(-20 * t)
        freq = 220 - 120 * (i / num_samples)
        sine = math.sin(2 * math.pi * freq * t)
        square = 1.0 if sine > 0 else -1.0
        noise = (random.random() * 2 - 1)
        sample = (square * 0.4 + noise * 0.6) * env
        samples.append(sample)

    return samples

def generate_sniper_shot():
    """Sniper shot: loud, heavy booming gunshot with tail."""
    sample_rate = 44100
    duration = 0.5
    num_samples = int(sample_rate * duration)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        env = math.exp(-10 * t)
        freq = 110 - 70 * (i / num_samples)
        sine = math.sin(2 * math.pi * freq * t)
        noise = (random.random() * 2 - 1)
        sample = (sine * 0.5 + noise * 0.5) * env
        samples.append(sample)

    return samples

def generate_reload_sound():
    """Magazine reload click sound."""
    sample_rate = 44100
    duration = 0.3
    num_samples = int(sample_rate * duration)
    samples = [0.0] * num_samples

    # First click (mag detach)
    click1_start = int(0.02 * sample_rate)
    click1_len = int(0.04 * sample_rate)
    for i in range(click1_len):
        t = i / sample_rate
        env = math.exp(-100 * t)
        sample = (random.random() * 2 - 1) * env * 0.7
        if click1_start + i < num_samples:
            samples[click1_start + i] += sample

    # Second click (mag insert / slide lock)
    click2_start = int(0.18 * sample_rate)
    click2_len = int(0.05 * sample_rate)
    for i in range(click2_len):
        t = i / sample_rate
        env = math.exp(-90 * t)
        sample = (random.random() * 2 - 1) * env * 0.9
        if click2_start + i < num_samples:
            samples[click2_start + i] += sample

    return samples

def generate_hit_sound():
    """Bullet impact hit marker tick."""
    sample_rate = 44100
    duration = 0.08
    num_samples = int(sample_rate * duration)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        env = math.exp(-50 * t)
        freq = 800 - 400 * (i / num_samples)
        sine = math.sin(2 * math.pi * freq * t)
        samples.append(sine * env * 0.8)

    return samples

def generate_wind_sound():
    """Looping ambient wind sound."""
    sample_rate = 44100
    duration = 3.0
    num_samples = int(sample_rate * duration)
    samples = []

    # Low pass filtered noise with low frequency sine mod
    prev = 0.0
    for i in range(num_samples):
        t = i / sample_rate
        noise = random.random() * 2 - 1
        # Simple low-pass filter
        filtered = prev + 0.1 * (noise - prev)
        prev = filtered

        # Modulate amplitude softly over time
        mod = 0.3 + 0.2 * math.sin(2 * math.pi * 0.5 * t)
        samples.append(filtered * mod * 0.5)

    return samples

def generate_all_audio():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    sounds = {
        "shot_pistol.wav": generate_pistol_shot(),
        "shot_rifle.wav": generate_rifle_shot(),
        "shot_sniper.wav": generate_sniper_shot(),
        "reload.wav": generate_reload_sound(),
        "hit.wav": generate_hit_sound(),
        "wind.wav": generate_wind_sound(),
    }

    for name, samples in sounds.items():
        path = os.path.join(AUDIO_DIR, name)
        generate_wav(path, samples)
        print(f"Generated {path} ({len(samples)} samples)")

if __name__ == "__main__":
    generate_all_audio()
