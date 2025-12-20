# Models module initialization
# Import all models here to ensure they're registered with SQLAlchemy

from app.models.user import User
from app.models.room_type import RoomType
from app.models.inventory import Inventory
from app.models.customer import Customer
from app.models.booking import Booking, BookingStatus

__all__ = [
    "User",
    "RoomType", 
    "Inventory",
    "Customer",
    "Booking",
    "BookingStatus"
]
