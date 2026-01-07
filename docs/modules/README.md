# Modules Reference

This directory contains detailed documentation for each PMS-CYNERZA module.

## Core Modules (Always Enabled)

| Module | Description | Documentation |
|--------|-------------|---------------|
| **Core** | Authentication, Users, Config | [core.md](./core.md) |
| **Room Types** | Room type management | [room-types.md](./room-types.md) |
| **Inventory** | Daily inventory tracking | [inventory.md](./inventory.md) |
| **Bookings** | Reservation management | [bookings.md](./bookings.md) |
| **Customers** | Guest profiles & VIP tracking | [customers.md](./customers.md) |

## Phase 1 Modules

| Module | Description | Min Tier | Documentation |
|--------|-------------|----------|---------------|
| **Dashboard** | Analytics & KPIs | Standard | [dashboard.md](./dashboard.md) |
| **Calendar** | Visual calendar view | Standard | [calendar.md](./calendar.md) |
| **Blocks** | Room blocks (maintenance, holds) | Professional | [blocks.md](./blocks.md) |
| **Allotments** | Group block management | Professional | [allotments.md](./allotments.md) |

## Phase 2 Modules

| Module | Description | Min Tier | Documentation |
|--------|-------------|----------|---------------|
| **Housekeeping** | Room status & task management | Standard | [housekeeping.md](./housekeeping.md) |
| **Night Audit** | Daily audit & reconciliation | Professional | [night-audit.md](./night-audit.md) |

## Phase 3 Modules (Planned)

| Module | Description | Min Tier | Documentation |
|--------|-------------|----------|---------------|
| Folio | Guest folios & charges | Professional | Coming soon |
| Invoicing | Invoice generation | Professional | Coming soon |
| Tax Engine | Tax calculations | Professional | Coming soon |
| Payments | Payment processing | Professional | Coming soon |

## Module Dependencies

```
Core ─┬─ Room Types ─── Inventory
      │
      └─ Customers ─── Bookings ─┬─ Dashboard
                                 ├─ Calendar
                                 ├─ Blocks
                                 ├─ Allotments
                                 ├─ Housekeeping
                                 └─ Night Audit
```
