'use client';

import { useQuery } from '@tanstack/react-query';
import { dashboardApi, TodaysActivity, ForecastAnalytics, QuickStats } from '@/lib/api/dashboard';

/**
 * Hook to fetch today's activity data
 * Returns arrivals, departures, in-house guests, and issues
 */
export function useTodaysActivity() {
    return useQuery<TodaysActivity, Error>({
        queryKey: ['dashboard', 'todays-activity'],
        queryFn: dashboardApi.getTodaysActivity,
        staleTime: 30000, // 30 seconds - refresh frequently for real-time data
        refetchInterval: 60000, // Auto-refresh every minute
    });
}

/**
 * Hook to fetch 14-day forecast data
 * Returns daily occupancy, revenue projections, and peak/low days
 */
export function useForecast() {
    return useQuery<ForecastAnalytics, Error>({
        queryKey: ['dashboard', 'forecast'],
        queryFn: dashboardApi.getForecast,
        staleTime: 300000, // 5 minutes - forecast doesn't change as frequently
    });
}

/**
 * Hook to fetch quick stats
 * Returns revenue metrics, ADR, RevPAR, and occupancy
 */
export function useQuickStats() {
    return useQuery<QuickStats, Error>({
        queryKey: ['dashboard', 'quick-stats'],
        queryFn: dashboardApi.getQuickStats,
        staleTime: 60000, // 1 minute
        refetchInterval: 120000, // Auto-refresh every 2 minutes
    });
}
