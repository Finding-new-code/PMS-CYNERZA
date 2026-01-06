'use client';

import {
  CreditCard,
  TrendingUp,
  DollarSign,
  Percent
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { RevenueChart } from '@/components/dashboard/revenue-chart';
import { RecentBookings } from '@/components/dashboard/recent-bookings';
import { TodaysActivityCard } from '@/components/dashboard/todays-activity-card';
import { ForecastChart } from '@/components/dashboard/forecast-chart';
import { QuickActions } from '@/components/dashboard/quick-actions';
import { useQuickStats } from '@/lib/hooks/use-dashboard';
import { useBookings } from '@/lib/hooks/use-bookings';
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardHome() {
  const { data: quickStats, isLoading: statsLoading } = useQuickStats();
  const { data: bookingsData, isLoading: bookingsLoading } = useBookings(1, 5);

  const recentBookings = Array.isArray(bookingsData) ? bookingsData.slice(0, 5) : [];

  const stats = [
    {
      title: 'Revenue Today',
      value: `$${quickStats?.revenue_today ? Number(quickStats.revenue_today).toLocaleString() : '0'}`,
      description: 'Current day earnings',
      icon: DollarSign,
    },
    {
      title: 'Revenue MTD',
      value: `$${quickStats?.revenue_mtd ? Number(quickStats.revenue_mtd).toLocaleString() : '0'}`,
      description: 'Month to date',
      icon: CreditCard,
    },
    {
      title: 'Occupancy',
      value: `${quickStats?.occupancy_today?.toFixed(1) || '0'}%`,
      description: 'Today\'s rate',
      icon: Percent,
    },
    {
      title: 'RevPAR',
      value: `$${quickStats?.revpar ? Number(quickStats.revpar).toFixed(2) : '0'}`,
      description: 'Revenue per room',
      icon: TrendingUp,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-950 dark:text-white">
            Dashboard
          </h1>
          <p className="text-zinc-500 dark:text-zinc-400">
            Welcome to PMS-CYNERZA. Here's what's happening today.
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Quick Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">
                    {stat.description}
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-4 lg:grid-cols-7">
        {/* 14-Day Forecast (spans 4 columns) */}
        <ForecastChart />

        {/* Today's Activity (spans 3 columns) */}
        <div className="lg:col-span-3">
          <TodaysActivityCard />
        </div>
      </div>

      {/* Secondary Content */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Revenue Overview</CardTitle>
            <CardDescription>
              Monthly revenue performance for the current year.
            </CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <RevenueChart />
          </CardContent>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Recent Bookings</CardTitle>
            <CardDescription>
              Latest booking transactions.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {bookingsLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : (
              <RecentBookings bookings={recentBookings} />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
