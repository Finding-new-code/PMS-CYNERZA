# Models module initialization
# Import all models here to ensure they're registered

from app.models.user import User
from app.models.room_type import RoomType
from app.models.inventory import Inventory
from app.models.customer import Customer
from app.models.booking import Booking, BookingStatus
from app.models.booking_item import BookingItem
from app.models.audit_log import AuditLog
from app.models.room_block import RoomBlock, BlockType, BlockStatus
from app.models.allotment import Allotment, AllotmentRoom, AllotmentStatus
from app.models.room import Room, RoomStatus, OccupancyStatus
from app.models.housekeeping_task import HousekeepingTask, TaskType, TaskStatus, TaskPriority
from app.models.night_audit import NightAudit, RoomCharge
from app.models.messaging import Message, MessageTemplate, Conversation, MessageChannel, MessageDirection, MessageStatus
from app.models.automation import AutomationRule, AutomationLog, TriggerType, AutomationStatus
from app.models.checkin import DigitalCheckIn, GuestDocument, CheckInStatus, DocumentType
from app.models.upsell import UpsellProduct, UpsellOrder, UpsellOrderItem, ProductCategory, OrderStatus

__all__ = [
    "User",
    "RoomType",
    "Inventory",
    "Booking",
    "BookingStatus",
    "BookingItem",
    "Customer",
    "AuditLog",
    "RoomBlock",
    "BlockType",
    "BlockStatus",
    "Allotment",
    "AllotmentRoom",
    "AllotmentStatus",
    "Room",
    "RoomStatus",
    "OccupancyStatus",
    "HousekeepingTask",
    "TaskType",
    "TaskStatus",
    "TaskPriority",
    "NightAudit",
    "RoomCharge",
]

