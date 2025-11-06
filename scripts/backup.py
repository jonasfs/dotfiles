#!/usr/bin/env python3
import os
import tarfile
from pathlib import Path
from datetime import datetime

SYMLINK_MAP = Path("scripts/common/symlinks.map")
BACKUP_DIR = Path("backups")


def parse_map_line(line: str):
    """Extract source and destination from 'src -> dest' format."""
    if "->" not in line:
        return None, None
    src, dest = line.split("->")
    return src.strip(), Path(os.path.expanduser(dest.strip()))


def create_backup():
    """
    Creates a timestamped tar.gz backup of pre-existing destination files.

    Returns:
        bool: True if backup successfully created or nothing needed backup,
              False if an error occurred.
    """
    try:
        # Ensure backup directory exists
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = BACKUP_DIR / f"backup_{timestamp}.tar.gz"

        # Track if at least one file was added
        any_backed_up = False

        with tarfile.open(backup_file, "w:gz") as tar:
            print(f"📦 Backup archive: {backup_file}")

            for line in SYMLINK_MAP.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                src, dest = parse_map_line(line)
                if not dest or not dest.exists():
                    continue

                print(f"Found existing file: {dest}")
                answer = input("Backup this file? [y/N]: ").strip().lower()

                if answer == "y":
                    tar.add(dest, arcname=dest.relative_to(Path.home()))
                    print(f"✅ Added to backup: {dest}")
                    any_backed_up = True
                else:
                    print("⏭️ Skipped.")

        if not any_backed_up:
            backup_file.unlink()  # delete empty tar
            print("ℹ️ No files were backed up; archive removed.")
            return True  # Still successful, just no backup needed

        print("\n🎉 Backup completed successfully!")
        print("🗂️ Restore with:")
        print(f"    tar -xzf {backup_file} -C $HOME")
        return True

    except Exception as e:
        print(f"❌ ERROR: Backup failed: {e}")
        return False


if __name__ == "__main__":
    success = create_backup()
    exit(0 if success else 1)
