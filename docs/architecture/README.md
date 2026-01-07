# Architecture Overview

## System Design Philosophy

PMS-CYNERZA follows a **modular, feature-flag driven architecture** that allows:

1. **Scalability** - From 5-room B&Bs to 500-room hotel chains
2. **Customization** - Enable/disable features per client
3. **Maintainability** - Independent modules with clear boundaries
4. **Extensibility** - Easy to add new features without affecting existing ones

## Project Structure

```
PMS-CYNERZA/
├── app/                          # Backend (FastAPI)
│   ├── core/                     # Core utilities
│   │   ├── config.py             # App configuration
│   │   ├── database.py           # Database connection
│   │   ├── security.py           # Auth & encryption
│   │   └── feature_flags.py      # Module toggles
│   │
│   ├── models/                   # SQLAlchemy models (per module)
│   │   ├── user.py               # Core
│   │   ├── room_type.py          # Core
│   │   ├── inventory.py          # Core
│   │   ├── booking.py            # Bookings
│   │   ├── customer.py           # Customers
│   │   ├── room.py               # Housekeeping
│   │   ├── housekeeping_task.py  # Housekeeping
│   │   ├── night_audit.py        # Night Audit
│   │   ├── room_block.py         # Blocks/Allotments
│   │   └── allotment.py          # Blocks/Allotments
│   │
│   ├── schemas/                  # Pydantic schemas (per module)
│   ├── services/                 # Business logic (per module)
│   ├── routers/                  # API endpoints (per module)
│   └── main.py                   # App initialization
│
├── pms-frontend/                 # Frontend (Next.js)
│   ├── app/                      # Pages & routes
│   ├── components/               # UI components (per module)
│   ├── lib/
│   │   ├── api/                  # API clients (per module)
│   │   └── hooks/                # React hooks (per module)
│   └── types/                    # TypeScript types
│
├── docs/                         # Documentation
└── config/                       # Configuration templates
```

## Module Independence

Each module follows this structure:

```
Module: Housekeeping
├── Model:    app/models/room.py, housekeeping_task.py
├── Schema:   app/schemas/housekeeping.py
├── Service:  app/services/housekeeping_service.py
├── Router:   app/routers/housekeeping.py
├── Frontend: pms-frontend/components/housekeeping/*
├── API Hook: pms-frontend/lib/hooks/use-housekeeping.ts
└── Docs:     docs/modules/housekeeping.md
```

## Client Tier Architecture

### Starter Tier (B&B, 1-10 rooms)
```python
# Minimal modules enabled
ENABLED_MODULES = ["core", "bookings", "customers"]
```

### Standard Tier (Boutique, 11-50 rooms)
```python
ENABLED_MODULES = [
    "core", "bookings", "customers",
    "dashboard", "housekeeping"
]
```

### Professional Tier (Mid-size, 51-200 rooms)
```python
ENABLED_MODULES = [
    "core", "bookings", "customers",
    "dashboard", "housekeeping",
    "night_audit", "allotments", "blocks"
]
```

### Enterprise Tier (Chains, 200+ rooms)
```python
ENABLED_MODULES = ["*"]  # All modules
MULTI_PROPERTY = True
```

## Database Strategy

- **Development/Starter**: SQLite (simple, file-based)
- **Production/Professional+**: PostgreSQL (scalable, concurrent)

```python
# config.py
if TIER == "starter":
    DATABASE_URL = "sqlite:///./hotel_pms.db"
else:
    DATABASE_URL = "postgresql://user:pass@host/db"
```

## API Design Patterns

All modules follow consistent patterns:

| Pattern | Example |
|---------|---------|
| List items | `GET /module/` |
| Get single | `GET /module/{id}` |
| Create | `POST /module/` |
| Update | `PATCH /module/{id}` |
| Delete | `DELETE /module/{id}` |
| Actions | `POST /module/{id}/action` |
