from .users import router as users_router
from .auth import router as auth_router

"""
Routers module for JagCoaching backend application.

This module contains API routers that handle different endpoints:
- users: User management endpoints
- auth: Authentication related endpoints
"""


# Export the routers to be included in the main FastAPI application
__all__ = ["users_router", "auth_router"]