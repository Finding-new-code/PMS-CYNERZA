'use client';

import { useState } from 'react';
import { format, addDays, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import {
    ChevronLeft,
    ChevronRight,
    Package,
    RefreshCw,
    Save,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Mock data for demo
const mockRoomTypes = [
    { id: 1, name: 'Deluxe Suite', total_rooms: 10, base_price: 5000 },
    { id: 2, name: 'Standard Room', total_rooms: 20, base_price: 2500 },
    { id: 3, name: 'Family Room', total_rooms: 8, base_price: 4000 },
    { id: 4, name: 'Economy Room', total_rooms: 15, base_price: 1500 },
];

// Generate mock inventory data
const generateMockInventory = (startDate: Date, endDate: Date) => {
    const days = eachDayOfInterval({ start: startDate, end: endDate });
    const inventory: Record<string, Record<number, { available: number; price: number }>> = {};

    days.forEach((day) => {
        const dateKey = format(day, 'yyyy-MM-dd');
        inventory[dateKey] = {};

        mockRoomTypes.forEach((rt) => {
            // Simulate varying availability
            const booked = Math.floor(Math.random() * rt.total_rooms * 0.7);
            inventory[dateKey][rt.id] = {
                available: rt.total_rooms - booked,
                price: rt.base_price + Math.floor(Math.random() * 500),
            };
        });
    });

    return inventory;
};

export default function InventoryPage() {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [editMode, setEditMode] = useState(false);

    const startDate = startOfMonth(currentMonth);
    const endDate = endOfMonth(currentMonth);
    const days = eachDayOfInterval({ start: startDate, end: endDate });

    const [inventory] = useState(() => generateMockInventory(startDate, addDays(endDate, 30)));

    const handlePrevMonth = () => {
        setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
    };

    const handleNextMonth = () => {
        setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0,
        }).format(value);
    };

    const getAvailabilityColor = (available: number, total: number) => {
        const percentage = (available / total) * 100;
        if (percentage === 0) return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
        if (percentage < 30) return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400';
        if (percentage < 70) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400';
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Inventory Management</h1>
                    <p className="text-muted-foreground">
                        Manage room availability and pricing by date
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setEditMode(!editMode)}>
                        {editMode ? <Save className="mr-2 h-4 w-4" /> : <Package className="mr-2 h-4 w-4" />}
                        {editMode ? 'Save Changes' : 'Edit Mode'}
                    </Button>
                    <Button variant="outline" size="sm">
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Regenerate
                    </Button>
                </div>
            </div>

            {/* Month Navigation */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="icon" onClick={handlePrevMonth}>
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <h2 className="text-xl font-semibold min-w-[200px] text-center">
                        {format(currentMonth, 'MMMM yyyy')}
                    </h2>
                    <Button variant="outline" size="icon" onClick={handleNextMonth}>
                        <ChevronRight className="h-4 w-4" />
                    </Button>
                </div>
                <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded bg-green-500"></div>
                        <span>Available (70%+)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded bg-yellow-500"></div>
                        <span>Limited (30-70%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded bg-orange-500"></div>
                        <span>Low (&lt;30%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded bg-red-500"></div>
                        <span>Sold Out</span>
                    </div>
                </div>
            </div>

            {/* Inventory Grid */}
            <Card>
                <CardContent className="p-0 overflow-x-auto">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="sticky left-0 bg-background z-10 min-w-[150px]">
                                    Room Type
                                </TableHead>
                                {days.map((day) => (
                                    <TableHead key={day.toISOString()} className="text-center min-w-[80px]">
                                        <div className="text-xs">{format(day, 'EEE')}</div>
                                        <div>{format(day, 'd')}</div>
                                    </TableHead>
                                ))}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {mockRoomTypes.map((roomType) => (
                                <TableRow key={roomType.id}>
                                    <TableCell className="sticky left-0 bg-background z-10 font-medium">
                                        <div>{roomType.name}</div>
                                        <div className="text-xs text-muted-foreground">
                                            {roomType.total_rooms} total
                                        </div>
                                    </TableCell>
                                    {days.map((day) => {
                                        const dateKey = format(day, 'yyyy-MM-dd');
                                        const inv = inventory[dateKey]?.[roomType.id] || { available: 0, price: roomType.base_price };

                                        return (
                                            <TableCell key={day.toISOString()} className="p-1 text-center">
                                                {editMode ? (
                                                    <div className="space-y-1">
                                                        <Input
                                                            type="number"
                                                            defaultValue={inv.available}
                                                            className="h-6 w-12 text-xs p-1 text-center mx-auto"
                                                        />
                                                        <Input
                                                            type="number"
                                                            defaultValue={inv.price}
                                                            className="h-6 w-16 text-xs p-1 text-center mx-auto"
                                                        />
                                                    </div>
                                                ) : (
                                                    <div
                                                        className={cn(
                                                            'rounded px-1 py-0.5 text-xs',
                                                            getAvailabilityColor(inv.available, roomType.total_rooms)
                                                        )}
                                                    >
                                                        <div className="font-medium">{inv.available}</div>
                                                        <div className="text-[10px] opacity-75">
                                                            {formatCurrency(inv.price)}
                                                        </div>
                                                    </div>
                                                )}
                                            </TableCell>
                                        );
                                    })}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-4">
                {mockRoomTypes.map((roomType) => {
                    const totalAvailable = days.reduce((sum, day) => {
                        const dateKey = format(day, 'yyyy-MM-dd');
                        return sum + (inventory[dateKey]?.[roomType.id]?.available || 0);
                    }, 0);
                    const avgAvailable = Math.round(totalAvailable / days.length);

                    return (
                        <Card key={roomType.id}>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium">{roomType.name}</CardTitle>
                                <CardDescription>{roomType.total_rooms} rooms total</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{avgAvailable}</div>
                                <p className="text-xs text-muted-foreground">
                                    Avg. available per day this month
                                </p>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}
