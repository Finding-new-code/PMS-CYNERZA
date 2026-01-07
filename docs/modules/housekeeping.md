# Housekeeping Module

> **Minimum Tier:** Standard  
> **Phase:** 2.1  
> **Status:** ✅ Complete

## Overview

The Housekeeping module enables hotels to track room cleanliness status, assign housekeeping staff, manage cleaning tasks, and generate housekeeping reports.

## Features

### Room Status Tracking
- **Tri-state housekeeping status:** Dirty → Clean → Inspected
- **Occupancy tracking:** Vacant, Occupied, Checkout, Checkin, Stayover
- **Priority assignment** for urgent cleaning
- **Housekeeper assignment** per room

### Task Management
- **Task types:** Checkout Clean, Stayover Clean, Inspection, Turndown, Deep Clean
- **Priority levels:** Low, Normal, High, Urgent
- **Task workflow:** Pending → In Progress → Completed
- **Supervisor inspection** with pass/fail tracking

### Automatic Triggers
- **Checkout reset:** Marks checkout rooms as Dirty
- **Daily reset (2 AM):** Resets for stayover cleaning

### Reports
- **Summary dashboard:** Room counts by status
- **Workload distribution:** Tasks per housekeeper
- **Completion metrics:** Tasks completed today

## API Endpoints

### Rooms

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/housekeeping/rooms` | List all rooms with filters |
| GET | `/housekeeping/rooms/{id}` | Get room details |
| POST | `/housekeeping/rooms` | Create new room |
| PATCH | `/housekeeping/rooms/{id}/status` | Update room status |
| POST | `/housekeeping/rooms/{id}/assign` | Assign housekeeper |
| POST | `/housekeeping/rooms/bulk-status-update` | Bulk status update |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/housekeeping/tasks` | List tasks with filters |
| POST | `/housekeeping/tasks` | Create task |
| POST | `/housekeeping/tasks/{id}/complete` | Mark complete |
| POST | `/housekeeping/tasks/{id}/inspect` | Record inspection |

### Reports & Triggers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/housekeeping/summary` | Status summary |
| POST | `/housekeeping/triggers/checkout-reset` | Trigger checkout reset |
| POST | `/housekeeping/triggers/daily-reset` | Trigger daily reset |

## Data Models

### Room
```python
class Room:
    id: int
    room_number: str         # "101", "201A"
    room_type_id: int
    floor: int
    housekeeping_status: RoomStatus  # dirty, clean, inspected
    occupancy_status: OccupancyStatus
    assigned_housekeeper_id: int
    priority: int            # Higher = more urgent
    housekeeping_notes: str
    last_cleaned_at: datetime
    last_inspected_at: datetime
```

### HousekeepingTask
```python
class HousekeepingTask:
    id: int
    room_id: int
    task_type: TaskType      # checkout_clean, stayover_clean, etc.
    task_status: TaskStatus  # pending, in_progress, completed
    priority: TaskPriority   # low, normal, high, urgent
    assigned_to_id: int
    scheduled_date: datetime
    completed_at: datetime
    completion_notes: str
    inspection_passed: bool
```

## Frontend Components

```
pms-frontend/components/housekeeping/
├── room-status-board.tsx     # Visual board of room statuses
├── room-card.tsx             # Individual room card
├── task-list.tsx             # Task list view
├── task-form.tsx             # Create/edit task form
├── housekeeping-dashboard.tsx # Summary dashboard
└── housekeeper-workload.tsx  # Staff workload view
```

## Configuration

### Enable Module
```env
NEXT_PUBLIC_FEATURE_HOUSEKEEPING=true
```

### Customization Options
```python
# Housekeeping settings
HOUSEKEEPING_AUTO_RESET_TIME = "02:00"  # Daily reset time
HOUSEKEEPING_CHECKOUT_AUTO_DIRTY = True # Auto-mark checkout as dirty
HOUSEKEEPING_REQUIRE_INSPECTION = True  # Require supervisor inspection
```

## Usage Examples

### Update Room Status
```bash
curl -X PATCH http://localhost:8000/housekeeping/rooms/1/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"housekeeping_status": "clean", "notes": "Deep cleaned"}'
```

### Create Cleaning Task
```bash
curl -X POST http://localhost:8000/housekeeping/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "task_type": "checkout_clean",
    "priority": "high",
    "scheduled_date": "2026-01-08T10:00:00",
    "notes": "VIP checkout"
  }'
```

### Get Summary Report
```bash
curl http://localhost:8000/housekeeping/summary \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "total_rooms": 50,
  "dirty": 15,
  "clean": 30,
  "inspected": 5,
  "pending_tasks": 10,
  "completed_today": 25
}
```

## Files Reference

| File | Purpose |
|------|---------|
| `app/models/room.py` | Room model & enums |
| `app/models/housekeeping_task.py` | Task model |
| `app/schemas/housekeeping.py` | Pydantic schemas |
| `app/services/housekeeping_service.py` | Business logic |
| `app/routers/housekeeping.py` | API endpoints |
