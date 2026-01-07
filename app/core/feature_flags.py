"""
Feature Flags System for PMS-CYNERZA.
Enables/disables modules based on client tier and configuration.
"""

from enum import Enum
from typing import Set, Dict
from functools import lru_cache

from app.core.config import get_settings


class ClientTier(str, Enum):
    """Client subscription tier levels."""
    STARTER = "starter"         # B&B, 1-10 rooms
    STANDARD = "standard"       # Boutique, 11-50 rooms
    PROFESSIONAL = "professional"  # Mid-size, 51-200 rooms
    ENTERPRISE = "enterprise"   # Chains, 200+ rooms


class Module(str, Enum):
    """Available system modules."""
    # Core (always enabled)
    CORE = "core"
    ROOM_TYPES = "room_types"
    INVENTORY = "inventory"
    BOOKINGS = "bookings"
    CUSTOMERS = "customers"
    
    # Phase 1
    DASHBOARD = "dashboard"
    CALENDAR = "calendar"
    BLOCKS = "blocks"
    ALLOTMENTS = "allotments"
    
    # Phase 2
    HOUSEKEEPING = "housekeeping"
    NIGHT_AUDIT = "night_audit"
    
    # Phase 3 (Future)
    FOLIO = "folio"
    INVOICING = "invoicing"
    TAX_ENGINE = "tax_engine"
    PAYMENTS = "payments"


# Module definitions per tier
TIER_MODULES: Dict[ClientTier, Set[Module]] = {
    ClientTier.STARTER: {
        Module.CORE,
        Module.ROOM_TYPES,
        Module.INVENTORY,
        Module.BOOKINGS,
        Module.CUSTOMERS,
    },
    ClientTier.STANDARD: {
        Module.CORE,
        Module.ROOM_TYPES,
        Module.INVENTORY,
        Module.BOOKINGS,
        Module.CUSTOMERS,
        Module.DASHBOARD,
        Module.CALENDAR,
        Module.HOUSEKEEPING,
    },
    ClientTier.PROFESSIONAL: {
        Module.CORE,
        Module.ROOM_TYPES,
        Module.INVENTORY,
        Module.BOOKINGS,
        Module.CUSTOMERS,
        Module.DASHBOARD,
        Module.CALENDAR,
        Module.HOUSEKEEPING,
        Module.BLOCKS,
        Module.ALLOTMENTS,
        Module.NIGHT_AUDIT,
    },
    ClientTier.ENTERPRISE: {
        # All modules
        module for module in Module
    }
}


@lru_cache()
def get_client_tier() -> ClientTier:
    """Get the configured client tier from settings."""
    settings = get_settings()
    tier_str = getattr(settings, 'client_tier', 'professional')
    try:
        return ClientTier(tier_str.lower())
    except ValueError:
        return ClientTier.PROFESSIONAL  # Default


def get_enabled_modules(tier: ClientTier = None) -> Set[Module]:
    """Get enabled modules for the specified or current tier."""
    if tier is None:
        tier = get_client_tier()
    return TIER_MODULES.get(tier, TIER_MODULES[ClientTier.STARTER])


def is_module_enabled(module: Module, tier: ClientTier = None) -> bool:
    """Check if a specific module is enabled."""
    enabled = get_enabled_modules(tier)
    return module in enabled


def get_module_tier_requirement(module: Module) -> ClientTier:
    """Get the minimum tier required for a module."""
    for tier in [ClientTier.STARTER, ClientTier.STANDARD, 
                 ClientTier.PROFESSIONAL, ClientTier.ENTERPRISE]:
        if module in TIER_MODULES[tier]:
            return tier
    return ClientTier.ENTERPRISE


# Convenience functions for specific modules
def is_housekeeping_enabled() -> bool:
    return is_module_enabled(Module.HOUSEKEEPING)


def is_night_audit_enabled() -> bool:
    return is_module_enabled(Module.NIGHT_AUDIT)


def is_allotments_enabled() -> bool:
    return is_module_enabled(Module.ALLOTMENTS)


def is_blocks_enabled() -> bool:
    return is_module_enabled(Module.BLOCKS)
