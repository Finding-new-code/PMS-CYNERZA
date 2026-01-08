import { apiClient } from './client';

// Types for Night Audit API
export interface NightAudit {
    id: number;
    business_date: string;
    started_at: string;
    completed_at?: string;
    is_completed: boolean;
    total_room_revenue: number;
    total_other_revenue: number;
    total_tax: number;
    total_payments: number;
    rooms_occupied: number;
    rooms_available: number;
    rooms_out_of_service: number;
    occupancy_percentage: number;
    no_shows_processed: number;
    no_show_revenue_lost: number;
    room_charges_posted: number;
    notes?: string;
    errors?: string[];
    run_by_id: number;
    created_at: string;
}

export interface ReconciliationReport {
    business_date: string;
    total_revenue: number;
    total_payments: number;
    discrepancy: number;
    room_revenue_breakdown: {
        room_type: string;
        revenue: number;
        nights: number;
    }[];
}

export interface NightAuditTrigger {
    business_date?: string;
}

// Night Audit API functions
export const nightAuditApi = {
    runAudit: async (businessDate?: string) => {
        const payload: NightAuditTrigger = businessDate ? { business_date: businessDate } : {};
        const { data } = await apiClient.post<NightAudit>('/night-audit/run', payload);
        return data;
    },

    listAudits: async (limit: number = 30, offset: number = 0) => {
        const { data } = await apiClient.get<NightAudit[]>('/night-audit/audits', {
            params: { limit, offset },
        });
        return data;
    },

    getAudit: async (businessDate: string) => {
        const { data } = await apiClient.get<NightAudit>(`/night-audit/audits/${businessDate}`);
        return data;
    },

    getLatest: async () => {
        const { data } = await apiClient.get<NightAudit>('/night-audit/latest');
        return data;
    },

    getReconciliation: async (businessDate: string) => {
        const { data } = await apiClient.get<ReconciliationReport>(
            `/night-audit/reports/reconciliation/${businessDate}`
        );
        return data;
    },
};
