__all__ = [
    'user_router',
    'admin_router',
    'staff_router',
]

from .user import user_router
from .admin import admin_router
from .staff import staff_router