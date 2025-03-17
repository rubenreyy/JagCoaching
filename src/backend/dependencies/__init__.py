"""
Dependencies module for JagCoaching backend.

This module contains dependency functions used across the application,
primarily for authentication and user verification.
"""

from .auth import (
    get_current_user,
    get_current_active_user
)

__all__ = [
    "get_current_user",
    "get_current_active_user"
]