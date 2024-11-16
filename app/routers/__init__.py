__all__ = [
    'user_router',
    'admin_router',
    'staff_router',
    'vet_router',
    'volunteer_router'
]

from .user import user_router
from .admin import admin_router
from .staff import staff_router
from .vet import vet_router
from .volunteer import volunteer_router