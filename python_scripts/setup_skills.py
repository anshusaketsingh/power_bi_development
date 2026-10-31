"""Clone or update Microsoft's Skills for Fabric repository.

Reads SKILLS_REPO_URL and SKILLS_PATH from .env (with sane defaults) and
clones the repo if missing, otherwise pulls the latest changes.

Usage:
    source venv/bin/activate && python python_scripts/setup_skills.py
"""
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

url = os.getenv("SKILLS_REPO_URL", "https://github.com/microsoft/skills-for-fabric.git")
target = ROOT / os.getenv("SKILLS_PATH", "skills-for-fabric")

if (target / ".git").exists():
    print(f"Updating {target} ...")
    cmd = ["git", "-C", str(target), "pull", "--ff-only"]
else:
    print(f"Cloning {url} into {target} ...")
    cmd = ["git", "clone", "--depth", "1", url, str(target)]

sys.exit(subprocess.call(cmd))
