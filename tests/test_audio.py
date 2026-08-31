import os
import wave
import pytest
from audio_generator import generate_all_audio, AUDIO_DIR

def test_audio_generation(tmp_path):
    generate_all_audio()
    expected_files = ["shot_pistol.wav", "shot_rifle.wav", "shot_sniper.wav", "reload.wav", "hit.wav", "wind.wav"]

    for filename in expected_files:
        filepath = os.path.join(AUDIO_DIR, filename)
        assert os.path.exists(filepath), f"Audio file {filename} was not generated."
        assert os.path.getsize(filepath) > 44, f"Audio file {filename} is empty or invalid WAV."

        # Verify valid WAV format
        with wave.open(filepath, 'rb') as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == 44100
            assert wav_file.getnframes() > 0
