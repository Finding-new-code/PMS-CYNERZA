# Feature Flags & Customization

## Overview

PMS-CYNERZA uses a feature flag system to enable/disable modules based on client needs and subscription tier.

## Configuration

### Environment Variables

```env
# .env file
PMS_TIER=professional          # starter, standard, professional, enterprise
PMS_MODULES=housekeeping,night_audit,allotments
PMS_MULTI_PROPERTY=false
PMS_MAX_ROOMS=100
```

### Feature Flags Configuration

Create `config/features.py` or modify `.env`:

```python
# config/features.py
from enum import Enum
from typing import List, Set

class ClientTier(str, Enum):
    STARTER = "starter"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

# Module definitions
TIER_MODULES = {
    ClientTier.STARTER: {
        "core", "bookings", "customers", "inventory"
    },
    ClientTier.STANDARD: {
        "core", "bookings", "customers", "inventory",
        "dashboard", "calendar", "housekeeping"
    },
    ClientTier.PROFESSIONAL: {
        "core", "bookings", "customers", "inventory",
        "dashboard", "calendar", "housekeeping",
        "night_audit", "blocks", "allotments"
    },
    ClientTier.ENTERPRISE: {
        "*"  # All modules
    }
}

def get_enabled_modules(tier: ClientTier) -> Set[str]:
    """Get enabled modules for a client tier."""
    if tier == ClientTier.ENTERPRISE:
        return {"*"}  # All modules
    return TIER_MODULES.get(tier, set())

def is_module_enabled(module_name: str, tier: ClientTier) -> bool:
    """Check if a module is enabled for the given tier."""
    modules = get_enabled_modules(tier)
    return "*" in modules or module_name in modules
```

## Module Registration

### Backend (FastAPI)

```python
# app/main.py
from app.core.config import get_settings
from app.core.feature_flags import is_module_enabled

settings = get_settings()

# Conditionally include routers based on tier
if is_module_enabled("housekeeping", settings.tier):
    from app.routers.housekeeping import router as housekeeping_router
    app.include_router(housekeeping_router)

if is_module_enabled("night_audit", settings.tier):
    from app.routers.night_audit import router as night_audit_router
    app.include_router(night_audit_router)
```

### Frontend (Next.js)

```typescript
// lib/config/features.ts
export const FEATURES = {
  housekeeping: process.env.NEXT_PUBLIC_FEATURE_HOUSEKEEPING === 'true',
  nightAudit: process.env.NEXT_PUBLIC_FEATURE_NIGHT_AUDIT === 'true',
  allotments: process.env.NEXT_PUBLIC_FEATURE_ALLOTMENTS === 'true',
  multiProperty: process.env.NEXT_PUBLIC_MULTI_PROPERTY === 'true',
};

// Usage in components
import { FEATURES } from '@/lib/config/features';

export function Sidebar() {
  return (
    <nav>
      <Link href="/dashboard">Dashboard</Link>
      {FEATURES.housekeeping && <Link href="/housekeeping">Housekeeping</Link>}
      {FEATURES.nightAudit && <Link href="/night-audit">Night Audit</Link>}
    </nav>
  );
}
```

## Client Customization Examples

### Example 1: Small B&B (10 rooms)

```env
# .env
PMS_TIER=starter
PMS_MODULES=core,bookings,customers
PMS_MAX_ROOMS=10
```

**Enabled Features:**
- Room types & basic inventory
- Simple booking management
- Customer database
- Basic reports

### Example 2: Boutique Hotel (40 rooms)

```env
PMS_TIER=standard
PMS_MODULES=core,bookings,customers,dashboard,housekeeping
PMS_MAX_ROOMS=50
```

**Enabled Features:**
- Everything in Starter, plus:
- Enhanced dashboard with forecast
- Housekeeping management
- Room status tracking

### Example 3: City Hotel (150 rooms)

```env
PMS_TIER=professional
PMS_MODULES=core,bookings,customers,dashboard,housekeeping,night_audit,allotments
PMS_MAX_ROOMS=200
```

**Enabled Features:**
- Everything in Standard, plus:
- Night audit system
- Group allotments
- Room blocks management
- Advanced reporting

### Example 4: Hotel Chain (Multi-property)

```env
PMS_TIER=enterprise
PMS_MODULES=*
PMS_MULTI_PROPERTY=true
PMS_PROPERTIES=hotel-a,hotel-b,hotel-c
```

## Custom Branding

```env
# Branding
PMS_BRAND_NAME=MyHotel PMS
PMS_BRAND_LOGO=/assets/logo.png
PMS_PRIMARY_COLOR=#4F46E5
PMS_THEME=indigo
```

## Database Selection

```env
# For Starter tier (SQLite)
DATABASE_URL=sqlite:///./hotel_pms.db

# For Professional+ (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/pms_db
```
