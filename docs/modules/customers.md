# Customers Module

> **Minimum Tier:** Starter  
> **Phase:** 1.3 (Enhanced)  
> **Status:** ✅ Complete

## Overview

The Customers module manages guest profiles with VIP tracking, lifetime value calculation, profile merging, and preference management.

## Features

### Guest Profiles
- **Contact information** (name, email, phone, address)
- **ID verification** (passport, driver's license)
- **VIP status** with special notes
- **Preferences** storage (room type, dietary, etc.)

### VIP Management
- **VIP flag** for priority guests
- **VIP notes** for special handling
- **Lifetime value** tracking
- **Total stays** counter

### Profile Management
- **Duplicate detection** by email/phone
- **Profile merge** for deduplication
- **Booking history** view

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers` | List all customers |
| GET | `/customers/{id}` | Get customer with booking history |
| POST | `/customers` | Create new customer |
| PATCH | `/customers/{id}` | Update customer |
| PATCH | `/customers/{id}/vip` | Update VIP status |
| GET | `/customers/{id}/duplicates` | Find potential duplicates |
| POST | `/customers/merge` | Merge duplicate profiles |
| POST | `/customers/{id}/recalculate-ltv` | Recalculate lifetime value |

## Data Model

```python
class Customer:
    id: int
    name: str
    email: str
    phone: str
    address: str
    id_proof_type: str      # passport, driver_license
    id_proof_number: str
    
    # VIP fields
    is_vip: bool
    vip_notes: str          # Special preferences
    lifetime_value: Decimal # Total spend
    total_stays: int
    
    # Notes
    notes: str              # Staff notes
    preferences: str        # Guest preferences
```

## Usage Example

### Create VIP Customer
```bash
curl -X POST http://localhost:8000/customers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "+1234567890",
    "is_vip": true,
    "vip_notes": "Prefers ocean view",
    "preferences": "Non-smoking, high floor"
  }'
```

## Files Reference

| File | Purpose |
|------|---------|
| `app/models/customer.py` | Customer model |
| `app/schemas/customer.py` | Pydantic schemas |
| `app/services/guest_service.py` | VIP & merge logic |
| `app/routers/customer.py` | API endpoints |
