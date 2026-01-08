'use client';

import { useState } from 'react';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    Calendar,
    Users,
    BarChart3,
    Loader2,
} from 'lucide-react';
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Line, LineChart } from 'recharts';

// Mock data for demo mode
const mockOverview = {
    total_bookings: 156,
    confirmed_bookings: 142,
    cancelled_bookings: 14,
    total_revenue: 4325000,
    average_daily_rate: 2850,
    occupancy_rate: 78.5,
};

const mockDailyRevenue = Array.from({ length: 30 }, (_, i) => ({
    date: format(subDays(new Date(), 29 - i), 'MMM dd'),
    revenue: Math.floor(Math.random() * 50000) + 100000,
    booking_count: Math.floor(Math.random() * 10) + 5,
}));

const mockRoomTypes = [
    { room_type_name: 'Deluxe Suite', total_rooms_booked: 85, total_revenue: 2125000, booking_share_percentage: 45.2 },
    { room_type_name: 'Standard Room', total_rooms_booked: 120, total_revenue: 1200000, booking_share_percentage: 32.1 },
    { room_type_name: 'Family Room', total_rooms_booked: 42, total_revenue: 630000, booking_share_percentage: 15.4 },
    { room_type_name: 'Economy Room', total_rooms_booked: 28, total_revenue: 370000, booking_share_percentage: 7.3 },
];

export default function AnalyticsPage() {
    const [dateRange] = useState({
        start: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
        end: format(endOfMonth(new Date()), 'yyyy-MM-dd'),
    });
    const [isLoading] = useState(false);

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(value);
    };

    if (isLoading) {
        return (
            <div className="flex h-[400px] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
                    <p className="text-muted-foreground">
                        Business intelligence and performance metrics
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                        <Calendar className="mr-2 h-4 w-4" />
                        {format(new Date(dateRange.start), 'MMM d')} - {format(new Date(dateRange.end), 'MMM d, yyyy')}
                    </Button>
                </div>
            </div>

            {/* Overview KPIs */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{formatCurrency(mockOverview.total_revenue)}</div>
                        <p className="text-xs text-muted-foreground flex items-center">
                            <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                            +12.5% from last month
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{mockOverview.total_bookings}</div>
                        <p className="text-xs text-muted-foreground">
                            {mockOverview.confirmed_bookings} confirmed, {mockOverview.cancelled_bookings} cancelled
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Average Daily Rate</CardTitle>
                        <BarChart3 className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{formatCurrency(mockOverview.average_daily_rate)}</div>
                        <p className="text-xs text-muted-foreground flex items-center">
                            <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                            +5.2% from last month
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Occupancy Rate</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{mockOverview.occupancy_rate}%</div>
                        <p className="text-xs text-muted-foreground flex items-center">
                            <TrendingDown className="h-3 w-3 mr-1 text-red-500" />
                            -2.1% from last month
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Revenue Chart */}
            <div className="grid gap-4 md:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Revenue Trend</CardTitle>
                        <CardDescription>Daily revenue for the selected period</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={mockDailyRevenue}>
                                <XAxis dataKey="date" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${v / 1000}k`} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'var(--background)', border: '1px solid var(--border)' }}
                                    formatter={(value) => [formatCurrency(Number(value)), 'Revenue']}
                                />
                                <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Room Type Performance</CardTitle>
                        <CardDescription>Revenue by room category</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {mockRoomTypes.map((rt) => (
                                <div key={rt.room_type_name} className="flex items-center">
                                    <div className="flex-1 space-y-1">
                                        <p className="text-sm font-medium leading-none">{rt.room_type_name}</p>
                                        <p className="text-sm text-muted-foreground">
                                            {rt.total_rooms_booked} bookings
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-medium">{formatCurrency(rt.total_revenue)}</p>
                                        <p className="text-xs text-muted-foreground">{rt.booking_share_percentage}%</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Booking Trends */}
            <Card>
                <CardHeader>
                    <CardTitle>Booking Trends</CardTitle>
                    <CardDescription>Daily bookings and cancellations</CardDescription>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={mockDailyRevenue}>
                            <XAxis dataKey="date" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis fontSize={12} tickLine={false} axisLine={false} />
                            <Tooltip contentStyle={{ backgroundColor: 'var(--background)', border: '1px solid var(--border)' }} />
                            <Line type="monotone" dataKey="booking_count" stroke="#6366f1" strokeWidth={2} dot={false} />
                        </LineChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>
        </div>
    );
}
