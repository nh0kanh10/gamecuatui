"""
Multi-Game Mode Support
Core architecture: User Decision → AI Response
"""

from .base_game import BaseGame
from .last_voyage.game import LastVoyageGame
from .cultivation_sim.game import CultivationSimGame

__all__ = ['BaseGame', 'LastVoyageGame', 'CultivationSimGame']

