'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Sparkles,
    CheckCircle2,
    Clock,
    AlertCircle,
    Users,
    BedDouble,
    RotateCcw,
} from 'lucide-react';
import { cn } from '@/lib/utils';

type RoomStatus = 'clean' | 'dirty' | 'inspected' | 'out_of_service';
type OccupancyStatus = 'vacant' | 'occupied' | 'checkout' | 'arrival';

interface Room {
    id: number;
    room_number: string;
    floor: number;
    status: RoomStatus;
    occupancy: OccupancyStatus;
    room_type: string;
}

// Mock rooms data
const mockRooms: Room[] = [
    { id: 1, room_number: '101', floor: 1, status: 'clean', occupancy: 'vacant', room_type: 'Standard' },
    { id: 2, room_number: '102', floor: 1, status: 'dirty', occupancy: 'checkout', room_type: 'Standard' },
    { id: 3, room_number: '103', floor: 1, status: 'inspected', occupancy: 'occupied', room_type: 'Deluxe' },
    { id: 4, room_number: '104', floor: 1, status: 'clean', occupancy: 'arrival', room_type: 'Standard' },
    { id: 5, room_number: '105', floor: 1, status: 'out_of_service', occupancy: 'vacant', room_type: 'Family' },
    { id: 6, room_number: '201', floor: 2, status: 'dirty', occupancy: 'checkout', room_type: 'Deluxe' },
    { id: 7, room_number: '202', floor: 2, status: 'clean', occupancy: 'occupied', room_type: 'Suite' },
    { id: 8, room_number: '203', floor: 2, status: 'dirty', occupancy: 'vacant', room_type: 'Standard' },
    { id: 9, room_number: '204', floor: 2, status: 'inspected', occupancy: 'vacant', room_type: 'Deluxe' },
    { id: 10, room_number: '205', floor: 2, status: 'clean', occupancy: 'occupied', room_type: 'Family' },
    { id: 11, room_number: '301', floor: 3, status: 'clean', occupancy: 'vacant', room_type: 'Suite' },
    { id: 12, room_number: '302', floor: 3, status: 'dirty', occupancy: 'checkout', room_type: 'Suite' },
];

const statusConfig = {
    clean: { label: 'Clean', color: 'bg-green-500', icon: CheckCircle2 },
    dirty: { label: 'Dirty', color: 'bg-red-500', icon: AlertCircle },
    inspected: { label: 'Inspected', color: 'bg-blue-500', icon: Sparkles },
    out_of_service: { label: 'Out of Service', color: 'bg-gray-500', icon: Clock },
};

const occupancyConfig = {
    vacant: { label: 'Vacant', color: 'text-green-600 bg-green-50 dark:bg-green-900/30' },
    occupied: { label: 'Occupied', color: 'text-blue-600 bg-blue-50 dark:bg-blue-900/30' },
    checkout: { label: 'Checkout', color: 'text-orange-600 bg-orange-50 dark:bg-orange-900/30' },
    arrival: { label: 'Arrival', color: 'text-purple-600 bg-purple-50 dark:bg-purple-900/30' },
};

export default function HousekeepingPage() {
    const [rooms, setRooms] = useState(mockRooms);
    const [filter, setFilter] = useState<RoomStatus | 'all'>('all');

    const filteredRooms = filter === 'all' ? rooms : rooms.filter((r) => r.status === filter);

    const summary = {
        clean: rooms.filter((r) => r.status === 'clean').length,
        dirty: rooms.filter((r) => r.status === 'dirty').length,
        inspected: rooms.filter((r) => r.status === 'inspected').length,
        out_of_service: rooms.filter((r) => r.status === 'out_of_service').length,
    };

    const updateRoomStatus = (roomId: number, newStatus: RoomStatus) => {
        setRooms(rooms.map((r) => (r.id === roomId ? { ...r, status: newStatus } : r)));
    };

    const floors = [...new Set(rooms.map((r) => r.floor))].sort();

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Housekeeping</h1>
                    <p className="text-muted-foreground">
                        Manage room cleaning status and tasks
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                        <RotateCcw className="mr-2 h-4 w-4" />
                        Daily Reset
                    </Button>
                    <Button size="sm">
                        <Sparkles className="mr-2 h-4 w-4" />
                        Checkout Reset
                    </Button>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-4">
                {Object.entries(statusConfig).map(([status, config]) => {
                    const Icon = config.icon;
                    return (
                        <Card
                            key={status}
                            className={cn(
                                'cursor-pointer transition-all',
                                filter === status && 'ring-2 ring-indigo-500'
                            )}
                            onClick={() => setFilter(filter === status ? 'all' : (status as RoomStatus))}
                        >
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">{config.label}</CardTitle>
                                <div className={cn('h-3 w-3 rounded-full', config.color)} />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {summary[status as keyof typeof summary]}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    rooms
                                </p>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            {/* Room Grid by Floor */}
            {floors.map((floor) => (
                <Card key={floor}>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BedDouble className="h-5 w-5" />
                            Floor {floor}
                        </CardTitle>
                        <CardDescription>
                            {filteredRooms.filter((r) => r.floor === floor).length} rooms
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                            {filteredRooms
                                .filter((r) => r.floor === floor)
                                .map((room) => {
                                    const statusInfo = statusConfig[room.status];
                                    const occupancyInfo = occupancyConfig[room.occupancy];
                                    const StatusIcon = statusInfo.icon;

                                    return (
                                        <div
                                            key={room.id}
                                            className="border rounded-lg p-3 space-y-2 hover:bg-muted/50 transition-colors"
                                        >
                                            <div className="flex items-center justify-between">
                                                <span className="font-bold text-lg">{room.room_number}</span>
                                                <div className={cn('h-3 w-3 rounded-full', statusInfo.color)} />
                                            </div>
                                            <div className="text-xs text-muted-foreground">{room.room_type}</div>
                                            <Badge variant="secondary" className={cn('text-xs', occupancyInfo.color)}>
                                                {occupancyInfo.label}
                                            </Badge>
                                            <div className="flex gap-1 pt-1">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="h-6 w-6 p-0"
                                                    onClick={() => updateRoomStatus(room.id, 'clean')}
                                                    title="Mark Clean"
                                                >
                                                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="h-6 w-6 p-0"
                                                    onClick={() => updateRoomStatus(room.id, 'inspected')}
                                                    title="Mark Inspected"
                                                >
                                                    <Sparkles className="h-4 w-4 text-blue-500" />
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="h-6 w-6 p-0"
                                                    onClick={() => updateRoomStatus(room.id, 'dirty')}
                                                    title="Mark Dirty"
                                                >
                                                    <AlertCircle className="h-4 w-4 text-red-500" />
                                                </Button>
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
