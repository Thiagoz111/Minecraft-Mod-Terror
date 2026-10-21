"""Scratch directory for dev renders, audio QA spectrograms and caches (never committed).

DEADLINE_WORK overrides it; otherwise the first dev session's scratchpad while it still exists, else <repo>/.work.
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
_LEGACY = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'
WORK = os.environ.get('DEADLINE_WORK') or (_LEGACY if os.path.isdir(_LEGACY) else os.path.join(ROOT, '.work'))
os.makedirs(WORK, exist_ok=True)
