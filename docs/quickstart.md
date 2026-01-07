# Developer Quickstart Guide

## Setting Up a New Client

This guide walks through configuring PMS-CYNERZA for a new hospitality client.

## Step 1: Determine Client Tier

| Tier | Rooms | Use Case | Modules Included |
|------|-------|----------|------------------|
| **Starter** | 1-10 | B&B, Guesthouses | Core booking only |
| **Standard** | 11-50 | Boutique Hotels | + Housekeeping, Dashboard |
| **Professional** | 51-200 | City Hotels | + Night Audit, Allotments |
| **Enterprise** | 200+ | Hotel Chains | All modules |

## Step 2: Environment Configuration

### Backend (.env)

```bash
# Copy example and configure
cp .env.example .env.client
```

```env
# Client Configuration
CLIENT_NAME=MyHotel
CLIENT_TIER=professional

# Database (SQLite for dev, PostgreSQL for production)
DATABASE_URL=postgresql://user:pass@localhost:5432/myhotel_pms

# Features (optional overrides)
ENABLE_HOUSEKEEPING=true
ENABLE_NIGHT_AUDIT=true
ENABLE_ALLOTMENTS=true
ENABLE_BLOCKS=true

# Property limits
MAX_ROOMS=100
MAX_ROOM_TYPES=10
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=https://api.myhotel.com
NEXT_PUBLIC_APP_NAME=MyHotel PMS

# Feature flags
NEXT_PUBLIC_FEATURE_HOUSEKEEPING=true
NEXT_PUBLIC_FEATURE_NIGHT_AUDIT=true
NEXT_PUBLIC_FEATURE_ALLOTMENTS=true

# Branding
NEXT_PUBLIC_PRIMARY_COLOR=#4F46E5
NEXT_PUBLIC_LOGO_URL=/logos/myhotel.png
```

## Step 3: Database Setup

### Development (SQLite)
```bash
# Database auto-creates on first run
python -m uvicorn app.main:app --reload
```

### Production (PostgreSQL)
```bash
# Create database
createdb myhotel_pms

# Run migrations
alembic upgrade head
```

## Step 4: Customize Modules

### Enable/Disable in main.py

```python
# app/main.py
from app.core.feature_flags import is_module_enabled, Module

# Conditional router registration
if is_module_enabled(Module.HOUSEKEEPING):
    from app.routers.housekeeping import router as housekeeping_router
    app.include_router(housekeeping_router)

if is_module_enabled(Module.NIGHT_AUDIT):
    from app.routers.night_audit import router as night_audit_router
    app.include_router(night_audit_router)
```

### Frontend Sidebar

```tsx
// components/layout/sidebar.tsx
import { FEATURES } from '@/lib/config';

export function Sidebar() {
  return (
    <nav>
      <Link href="/dashboard">Dashboard</Link>
      <Link href="/bookings">Bookings</Link>
      
      {FEATURES.housekeeping && (
        <Link href="/housekeeping">Housekeeping</Link>
      )}
      
      {FEATURES.nightAudit && (
        <Link href="/night-audit">Night Audit</Link>
      )}
    </nav>
  );
}
```

## Step 5: Customize Branding

### Theme Colors
```tsx
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: process.env.NEXT_PUBLIC_PRIMARY_COLOR || '#4F46E5',
      }
    }
  }
}
```

### Logo & App Name
```tsx
// components/layout/header.tsx
const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'PMS-CYNERZA';
const LOGO_URL = process.env.NEXT_PUBLIC_LOGO_URL || '/logo.svg';
```

## Step 6: Deploy

### Docker Deployment
```yaml
# docker-compose.yml
services:
  backend:
    build: .
    environment:
      - CLIENT_TIER=professional
      - DATABASE_URL=postgresql://...
    ports:
      - "8000:8000"

  frontend:
    build: ./pms-frontend
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

### Vercel (Frontend)
```bash
cd pms-frontend
vercel --env-file .env.production
```

## Common Customizations

### Add Custom Fields
```python
# Extend customer model
class Customer(Base):
    # ... existing fields
    
    # Client-specific fields
    loyalty_number = Column(String(50))
    company_name = Column(String(200))
```

### Custom Reports
```python
# app/routers/custom_reports.py
@router.get("/reports/custom")
async def custom_report(db: AsyncSession = Depends(get_db)):
    # Client-specific logic
    pass
```

### Override Tax Calculations
```python
# app/services/custom_tax.py
def calculate_tax(amount: Decimal, region: str) -> Decimal:
    TAX_RATES = {
        "US-NY": 0.08875,
        "EU": 0.20,
        "IN": 0.18,
    }
    return amount * TAX_RATES.get(region, 0.10)
```

## Testing

```bash
# Backend tests
pytest tests/

# API test script
.\test-api.ps1

# Frontend tests
cd pms-frontend && npm test
```

## Support Matrix

| Feature | Starter | Standard | Professional | Enterprise |
|---------|---------|----------|--------------|------------|
| Max Rooms | 10 | 50 | 200 | Unlimited |
| Multi-property | ❌ | ❌ | ❌ | ✅ |
| API Rate Limit | 100/min | 500/min | 2000/min | Unlimited |
| Support | Email | Email | Priority | Dedicated |
