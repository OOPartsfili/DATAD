"""
This module defines the visual and auditory prompts that notify the
driver to take over control.
"""

import pygame


# --------------------------------------------------------------------- #
# Visual takeover prompt
# --------------------------------------------------------------------- #
def visual_takeover_prompt() -> None:
    """
    Display or log a visual message telling the driver to take over.
    (In a real application you would draw on‑screen graphics here.)
    """
    print("Visual takeover prompt")


# --------------------------------------------------------------------- #
# Auditory takeover prompt
# --------------------------------------------------------------------- #
def audio_takeover_prompt() -> None:
    """
    Play an audio clip that instructs the driver to take over.
    Replace the WAV file path below with your own sound file.
    """
    sound_file = "asset/takeover_prompt.wav"  # <-- update to your WAV path
    sound = pygame.mixer.Sound(sound_file)
    sound.play()
