'use client';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useForecast } from '@/lib/hooks/use-dashboard';
import {
    Area,
    AreaChart,
    ResponsiveContainer,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { TrendingUp, TrendingDown, Calendar } from 'lucide-react';

export function ForecastChart() {
    const { data, isLoading, error } = useForecast();

    if (error) {
        return (
            <Card className="col-span-4">
                <CardHeader>
                    <CardTitle>14-Day Forecast</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-red-500 text-sm">Failed to load forecast data</div>
                </CardContent>
            </Card>
        );
    }

    // Format data for chart
    const chartData = data?.forecast_days.map((day) => ({
        date: format(parseISO(day.date), 'MMM d'),
        fullDate: day.date,
        occupancy: day.occupancy_percent,
        revenue: day.projected_revenue,
        arrivals: day.arrivals,
        departures: day.departures,
        available: day.available_rooms,
        booked: day.booked_rooms,
    })) || [];

    return (
        <Card className="col-span-4">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <Calendar className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                            14-Day Forecast
                        </CardTitle>
                        <CardDescription>
                            Occupancy outlook for the next two weeks
                        </CardDescription>
                    </div>

                    {!isLoading && data && (
                        <div className="flex gap-4 text-sm">
                            <div className="text-center">
                                <p className="text-xs text-zinc-500">Avg Occupancy</p>
                                <p className="font-bold text-lg text-indigo-600 dark:text-indigo-400">
                                    {data.avg_occupancy}%
                                </p>
                            </div>
                            <div className="text-center">
                                <p className="text-xs text-zinc-500">Projected Revenue</p>
                                <p className="font-bold text-lg text-emerald-600 dark:text-emerald-400">
                                    ${Number(data.total_projected_revenue).toLocaleString()}
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </CardHeader>
            <CardContent>
                {isLoading ? (
                    <Skeleton className="h-[250px] w-full" />
                ) : (
                    <>
                        <ResponsiveContainer width="100%" height={250}>
                            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="occupancyGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" className="stroke-zinc-200 dark:stroke-zinc-700" />
                                <XAxis
                                    dataKey="date"
                                    tickLine={false}
                                    axisLine={false}
                                    className="text-xs fill-zinc-500"
                                />
                                <YAxis
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(value) => `${value}%`}
                                    className="text-xs fill-zinc-500"
                                    domain={[0, 100]}
                                />
                                <Tooltip
                                    content={({ active, payload }) => {
                                        if (active && payload && payload.length) {
                                            const data = payload[0].payload;
                                            return (
                                                <div className="bg-white dark:bg-zinc-800 rounded-lg shadow-lg border border-zinc-200 dark:border-zinc-700 p-3">
                                                    <p className="font-medium text-sm">{format(parseISO(data.fullDate), 'EEEE, MMM d')}</p>
                                                    <div className="mt-2 space-y-1 text-sm">
                                                        <p className="text-indigo-600 dark:text-indigo-400">
                                                            Occupancy: <span className="font-bold">{data.occupancy}%</span>
                                                        </p>
                                                        <p className="text-emerald-600 dark:text-emerald-400">
                                                            Revenue: <span className="font-bold">${Number(data.revenue).toLocaleString()}</span>
                                                        </p>
                                                        <p className="text-zinc-600 dark:text-zinc-400">
                                                            Rooms: {data.booked} booked, {data.available} available
                                                        </p>
                                                        <p className="text-zinc-600 dark:text-zinc-400">
                                                            Arrivals: {data.arrivals} | Departures: {data.departures}
                                                        </p>
                                                    </div>
                                                </div>
                                            );
                                        }
                                        return null;
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="occupancy"
                                    stroke="#6366f1"
                                    strokeWidth={2}
                                    fill="url(#occupancyGradient)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>

                        {/* Peak and Low Days */}
                        {data && (
                            <div className="flex gap-4 mt-4 pt-4 border-t border-zinc-200 dark:border-zinc-700">
                                {data.peak_day && (
                                    <div className="flex items-center gap-2 text-sm">
                                        <TrendingUp className="h-4 w-4 text-emerald-500" />
                                        <span className="text-zinc-500">Peak:</span>
                                        <span className="font-medium">{format(parseISO(data.peak_day), 'EEE, MMM d')}</span>
                                    </div>
                                )}
                                {data.lowest_day && (
                                    <div className="flex items-center gap-2 text-sm">
                                        <TrendingDown className="h-4 w-4 text-amber-500" />
                                        <span className="text-zinc-500">Lowest:</span>
                                        <span className="font-medium">{format(parseISO(data.lowest_day), 'EEE, MMM d')}</span>
                                    </div>
                                )}
                            </div>
                        )}
                    </>
                )}
            </CardContent>
        </Card>
    );
}
