"""
Multi-Game Mode Support
Core architecture: User Decision → AI Response
"""

from .base_game import BaseGame
from .last_voyage.game import LastVoyageGame
# Cultivation Simulator đã tách ra thành project riêng: cultivation-sim/

__all__ = ['BaseGame', 'LastVoyageGame']

