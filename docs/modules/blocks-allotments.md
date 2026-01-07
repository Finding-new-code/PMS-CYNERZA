# Blocks & Allotments Module

> **Minimum Tier:** Professional  
> **Phase:** 1.2  
> **Status:** ✅ Complete

## Overview

This module manages room blocks (maintenance, holds) and group allotments for corporate/event bookings.

## Blocks

### Use Cases
- **Maintenance blocks** - Rooms under repair
- **Out of service** - Temporarily unavailable
- **Holds** - Reserved for VIP/special requests
- **Renovations** - Long-term closure

### Block Statuses
- `ACTIVE` - Currently blocking rooms
- `RELEASED` - Block removed
- `EXPIRED` - Past end date

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/blocks/` | List blocks |
| POST | `/blocks/` | Create block |
| GET | `/blocks/{id}` | Get block details |
| PUT | `/blocks/{id}` | Update block |
| POST | `/blocks/{id}/release` | Release block early |
| DELETE | `/blocks/{id}` | Delete block |

## Allotments

### Use Cases
- **Corporate accounts** - Company room allocations
- **Wedding blocks** - Event room holds
- **Travel agencies** - Tour group reservations

### Allotment Statuses
- `TENTATIVE` - Preliminary hold
- `DEFINITE` - Confirmed allocation
- `RELEASED` - Rooms returned to inventory
- `CANCELLED` - Booking cancelled
- `PICKED_UP` - Fully booked

### Auto-Release Logic
Allotments can auto-release unsold rooms based on:
- **Cutoff date** - X days before arrival
- **Pickup threshold** - If below minimum %

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/allotments/` | List allotments |
| POST | `/allotments/` | Create allotment |
| GET | `/allotments/{id}` | Get allotment details |
| PATCH | `/allotments/{id}/status` | Update status |
| POST | `/allotments/{id}/pickup` | Record pickup |
| GET | `/allotments/{id}/report` | Pickup report |

## Data Models

### RoomBlock
```python
class RoomBlock:
    id: int
    room_type_id: int
    block_type: BlockType   # maintenance, hold, out_of_service
    start_date: date
    end_date: date
    rooms_blocked: int
    reason: str
    status: BlockStatus
```

### Allotment
```python
class Allotment:
    id: int
    name: str               # "Smith Wedding"
    group_code: str         # "SMITH2026"
    contact_name: str
    room_type_id: int
    start_date: date
    end_date: date
    rooms_allocated: int
    rooms_picked_up: int
    cutoff_date: date
    auto_release: bool
    status: AllotmentStatus
```

## Files Reference

| File | Purpose |
|------|---------|
| `app/models/room_block.py` | Block model |
| `app/models/allotment.py` | Allotment model |
| `app/schemas/block.py` | Block schemas |
| `app/schemas/allotment.py` | Allotment schemas |
| `app/services/block_service.py` | Block logic |
| `app/services/allotment_service.py` | Allotment logic |
| `app/routers/blocks.py` | Block API |
| `app/routers/allotments.py` | Allotment API |
