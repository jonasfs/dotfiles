#!/usr/bin/env python3
import os
import platform
from pathlib import Path

def detect_platform():
    system = platform.system().lower()
    if "windows" in system:
        return "windows"
    elif "darwin" in system:
        return "macos"
    else:
        return "linux"

def expand_path(path):
    return Path(os.path.expandvars(os.path.expanduser(path)))

def create_symlink(source, dest):
    dest_parent = dest.parent
    dest_parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() or dest.is_symlink():
        print(f"⚠️  Skipping existing: {dest}")
        return

    try:
        is_dir = source.is_dir()
        os.symlink(source, dest, target_is_directory=is_dir)
        print(f"✅ Linked {dest} -> {source}")
    except OSError as e:
        print(f"❌ Failed to link {dest}: {e}")

def parse_line(line):
    """Return (src, dst, [platforms]) or None if comment/invalid."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    platforms = []
    if "[" in line and "]" in line:
        main, tagpart = line.split("[", 1)
        platforms = [t.strip().lower() for t in tagpart.strip("[]").split(",")]
        line = main.strip()

    if "->" not in line:
        print(f"⚠️  Ignoring invalid line: {line}")
        return None

    src, dst = map(str.strip, line.split("->"))
    return src, dst, platforms

def main(symlinks_file="symlinks.map"):
    current_platform = detect_platform()
    print(f"🖥️  Detected platform: {current_platform}")

    lines = Path(symlinks_file).read_text().splitlines()
    for line in lines:
        parsed = parse_line(line)
        if not parsed:
            continue

        src, dst, platforms = parsed
        if platforms and current_platform not in platforms:
            continue

        source = expand_path(src).resolve()
        print(f"source:  {source}")
        dest = expand_path(dst)

        if not source.exists():
            print(f"⚠️  Source not found: {source}")
            continue

        # create_symlink(source, dest)

if __name__ == "__main__":
    import sys
    file = sys.argv[1] if len(sys.argv) > 1 else "symlinks.map"
    main(file)
