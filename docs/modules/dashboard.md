# Dashboard Module

> **Minimum Tier:** Standard  
> **Phase:** 1.1  
> **Status:** ✅ Complete

## Overview

The Dashboard module provides real-time analytics and KPIs for hotel operations, including today's activity, 14-day forecast, and quick statistics.

## Features

### Today's Activity Widget
- **Arrivals** expected today
- **Departures** expected today
- **In-House** guest count
- **Overbooking** warnings

### 14-Day Forecast
- **Occupancy percentage** per day
- **Revenue projection** per day
- **Peak day identification**
- **Visual chart display**

### Quick Stats
- **Revenue today** and month-to-date
- **Current occupancy rate**
- **RevPAR** (Revenue Per Available Room)
- **Average Daily Rate (ADR)**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/todays-activity` | Today's activity metrics |
| GET | `/dashboard/forecast` | 14-day occupancy/revenue forecast |
| GET | `/dashboard/quick-stats` | Key performance indicators |

## Response Examples

### Today's Activity
```json
{
  "arrivals_expected": 12,
  "arrivals_checked_in": 5,
  "departures_expected": 8,
  "departures_checked_out": 3,
  "in_house": 45,
  "overbookings": 0
}
```

### 14-Day Forecast
```json
{
  "forecast_days": [
    {"date": "2026-01-08", "occupancy_pct": 75.0, "revenue": 3750.00},
    {"date": "2026-01-09", "occupancy_pct": 82.0, "revenue": 4100.00}
  ],
  "peak_day": "2026-01-15",
  "avg_occupancy": 78.5
}
```

### Quick Stats
```json
{
  "revenue_today": 2500.00,
  "revenue_mtd": 45000.00,
  "occupancy_today": 85.0,
  "adr": 125.00,
  "revpar": 106.25
}
```

## Configuration

```env
NEXT_PUBLIC_FEATURE_DASHBOARD=true
```

## Files Reference

| File | Purpose |
|------|---------|
| `app/schemas/dashboard.py` | Response schemas |
| `app/services/dashboard_service.py` | Business logic |
| `app/routers/dashboard.py` | API endpoints |
