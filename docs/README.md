# PMS-CYNERZA Documentation

Comprehensive documentation for the PMS-CYNERZA Hotel Property Management System.

## Quick Links

- [Architecture Overview](./architecture/README.md)
- [Module Reference](./modules/README.md)
- [Feature Flags & Customization](./customization/README.md)
- [API Reference](./api/README.md)
- [Deployment Guide](./deployment/README.md)

## Target Clients

This platform is designed to scale for different hospitality businesses:

| Tier | Description | Typical Rooms | Recommended Modules |
|------|-------------|---------------|---------------------|
| **Starter** | B&B, Guesthouses | 1-10 rooms | Core, Bookings, Basic Reports |
| **Standard** | Boutique Hotels | 11-50 rooms | + Housekeeping, Dashboard |
| **Professional** | Mid-size Hotels | 51-200 rooms | + Night Audit, Allotments |
| **Enterprise** | Hotel Chains | 200+ rooms | All modules + Multi-property |

## Module Status

| Module | Status | Phase |
|--------|--------|-------|
| Core (Auth, Room Types) | ✅ Complete | - |
| Booking Engine | ✅ Complete | - |
| Customer Management | ✅ Complete | 1.3 |
| Dashboard & Analytics | ✅ Complete | 1.1 |
| Calendar & Inventory | ✅ Complete | 1.2 |
| Blocks & Allotments | ✅ Complete | 1.2 |
| Housekeeping | ✅ Complete | 2.1 |
| Night Audit | ✅ Complete | 2.2 |
| Folio System | 🚧 Planned | 3.1 |
| Invoicing | 🚧 Planned | 3.2 |
| Tax Engine | 🚧 Planned | 3.3 |
| Payment Processing | 🚧 Planned | 3.4 |

## Getting Started

1. Review [Architecture Overview](./architecture/README.md)
2. Configure [Feature Flags](./customization/feature-flags.md) for your client
3. Follow module-specific guides in [Modules](./modules/README.md)
