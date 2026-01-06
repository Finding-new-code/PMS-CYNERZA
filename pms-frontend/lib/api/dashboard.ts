import { apiClient } from './client';

// Types for Dashboard API responses
export interface TodaysActivity {
    arrivals_expected: number;
    arrivals_checked_in: number;
    arrivals_pending: number;
    departures_expected: number;
    departures_checked_out: number;
    departures_pending: number;
    in_house_guests: number;
    overbookings: number;
    cancellations_today: number;
    no_shows: number;
}

export interface ForecastDay {
    date: string;
    occupancy_percent: number;
    available_rooms: number;
    booked_rooms: number;
    projected_revenue: number;
    arrivals: number;
    departures: number;
}

export interface ForecastAnalytics {
    forecast_days: ForecastDay[];
    avg_occupancy: number;
    total_projected_revenue: number;
    peak_day: string | null;
    lowest_day: string | null;
}

export interface QuickStats {
    revenue_today: number;
    revenue_mtd: number;
    revenue_ytd: number;
    avg_daily_rate: number;
    revpar: number;
    occupancy_today: number;
}

// Dashboard API functions
export const dashboardApi = {
    getTodaysActivity: async (): Promise<TodaysActivity> => {
        const { data } = await apiClient.get<TodaysActivity>('/dashboard/todays-activity');
        return data;
    },

    getForecast: async (): Promise<ForecastAnalytics> => {
        const { data } = await apiClient.get<ForecastAnalytics>('/dashboard/forecast');
        return data;
    },

    getQuickStats: async (): Promise<QuickStats> => {
        const { data } = await apiClient.get<QuickStats>('/dashboard/quick-stats');
        return data;
    },
};
