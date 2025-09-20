"""
DeXteR - AI Assistant with Robot Arm Control

A comprehensive AI assistant that combines speech-to-text and large language models.
"""

__version__ = "0.1.0"
__author__ = "David Dominguez"

# Main package imports for easy access
from .core import llm, stt, prompts
from .utils import common

__all__ = ['llm', 'stt', 'prompts', 'common']
