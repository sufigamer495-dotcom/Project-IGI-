import os
import sys
import subprocess
from audio_generator import generate_all_audio

def build_executable():
    print("=== Step 1: Generating Audio Assets ===")
    generate_all_audio()

    print("\n=== Step 2: Packaging Executable with PyInstaller ===")
    spec_file = "game.spec"
    if not os.path.exists(spec_file):
        print(f"Error: {spec_file} not found!")
        sys.exit(1)

    cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--noconfirm", "--clean"]
    print("Running command:", " ".join(cmd))

    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\n=== Build Successful! Standalone executable bundle created in dist/ProjectIGI ===")
    else:
        print("\n=== Build Failed! PyInstaller exited with code", result.returncode)
        sys.exit(result.returncode)

if __name__ == "__main__":
    build_executable()
