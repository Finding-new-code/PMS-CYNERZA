# Routers module initialization

from app.routers.auth import router as auth_router
from app.routers.room_type import router as room_type_router
from app.routers.inventory import router as inventory_router
from app.routers.booking import router as booking_router
from app.routers.customer import router as customer_router

__all__ = [
    "auth_router",
    "room_type_router",
    "inventory_router",
    "booking_router",
    "customer_router"
]
