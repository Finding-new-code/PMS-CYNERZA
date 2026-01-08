'use client';

import { useState } from 'react';
import { format, subDays } from 'date-fns';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import {
    Moon,
    Play,
    CheckCircle2,
    AlertTriangle,
    DollarSign,
    BedDouble,
    TrendingUp,
    Clock,
    Loader2,
} from 'lucide-react';

// Mock Night Audit data
const mockAudits = Array.from({ length: 10 }, (_, i) => ({
    id: i + 1,
    business_date: format(subDays(new Date(), i + 1), 'yyyy-MM-dd'),
    started_at: format(subDays(new Date(), i + 1), "yyyy-MM-dd'T'02:00:00"),
    completed_at: format(subDays(new Date(), i + 1), "yyyy-MM-dd'T'02:15:00"),
    is_completed: true,
    total_room_revenue: Math.floor(Math.random() * 100000) + 150000,
    total_tax: Math.floor(Math.random() * 15000) + 20000,
    total_payments: Math.floor(Math.random() * 80000) + 120000,
    rooms_occupied: Math.floor(Math.random() * 20) + 30,
    rooms_available: 50,
    occupancy_percentage: Math.floor(Math.random() * 30) + 60,
    no_shows_processed: Math.floor(Math.random() * 3),
    room_charges_posted: Math.floor(Math.random() * 10) + 20,
}));

const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0,
    }).format(value);
};

export default function NightAuditPage() {
    const [audits] = useState(mockAudits);
    const [isRunning, setIsRunning] = useState(false);

    const latestAudit = audits[0];

    const handleRunAudit = () => {
        setIsRunning(true);
        setTimeout(() => {
            setIsRunning(false);
            // Would refresh audit list in real implementation
        }, 3000);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Night Audit</h1>
                    <p className="text-muted-foreground">
                        Daily financial reconciliation and reporting
                    </p>
                </div>
                <Button onClick={handleRunAudit} disabled={isRunning}>
                    {isRunning ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Running Audit...
                        </>
                    ) : (
                        <>
                            <Play className="mr-2 h-4 w-4" />
                            Run Night Audit
                        </>
                    )}
                </Button>
            </div>

            {/* Latest Audit Summary */}
            {latestAudit && (
                <Card className="border-indigo-200 bg-indigo-50/50 dark:border-indigo-900 dark:bg-indigo-950/20">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle className="flex items-center gap-2">
                                    <Moon className="h-5 w-5" />
                                    Latest Audit: {format(new Date(latestAudit.business_date), 'EEEE, MMMM d, yyyy')}
                                </CardTitle>
                                <CardDescription>
                                    Completed at {format(new Date(latestAudit.completed_at), 'HH:mm')}
                                </CardDescription>
                            </div>
                            <Badge className="bg-green-100 text-green-700">
                                <CheckCircle2 className="mr-1 h-3 w-3" />
                                Completed
                            </Badge>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="grid gap-4 md:grid-cols-4">
                            <div className="space-y-1">
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <DollarSign className="h-4 w-4" />
                                    Room Revenue
                                </div>
                                <div className="text-2xl font-bold">{formatCurrency(latestAudit.total_room_revenue)}</div>
                            </div>
                            <div className="space-y-1">
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <BedDouble className="h-4 w-4" />
                                    Rooms Occupied
                                </div>
                                <div className="text-2xl font-bold">
                                    {latestAudit.rooms_occupied}/{latestAudit.rooms_available}
                                </div>
                            </div>
                            <div className="space-y-1">
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <TrendingUp className="h-4 w-4" />
                                    Occupancy
                                </div>
                                <div className="text-2xl font-bold">{latestAudit.occupancy_percentage}%</div>
                            </div>
                            <div className="space-y-1">
                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Clock className="h-4 w-4" />
                                    Charges Posted
                                </div>
                                <div className="text-2xl font-bold">{latestAudit.room_charges_posted}</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Quick Stats */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Total Revenue (Last 7 Days)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {formatCurrency(audits.slice(0, 7).reduce((sum, a) => sum + a.total_room_revenue, 0))}
                        </div>
                        <p className="text-xs text-muted-foreground">From night audit records</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Average Occupancy</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {Math.round(audits.slice(0, 7).reduce((sum, a) => sum + a.occupancy_percentage, 0) / 7)}%
                        </div>
                        <p className="text-xs text-muted-foreground">Last 7 days average</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">No-Shows</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {audits.slice(0, 7).reduce((sum, a) => sum + a.no_shows_processed, 0)}
                        </div>
                        <p className="text-xs text-muted-foreground">Processed last 7 days</p>
                    </CardContent>
                </Card>
            </div>

            {/* Audit History */}
            <Card>
                <CardHeader>
                    <CardTitle>Audit History</CardTitle>
                    <CardDescription>Past night audit records and reconciliation data</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Business Date</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">Room Revenue</TableHead>
                                <TableHead className="text-right">Tax</TableHead>
                                <TableHead className="text-right">Occupancy</TableHead>
                                <TableHead className="text-right">No-Shows</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {audits.map((audit) => (
                                <TableRow key={audit.id} className="cursor-pointer hover:bg-muted/50">
                                    <TableCell className="font-medium">
                                        {format(new Date(audit.business_date), 'MMM d, yyyy')}
                                    </TableCell>
                                    <TableCell>
                                        {audit.is_completed ? (
                                            <Badge variant="secondary" className="bg-green-50 text-green-700">
                                                <CheckCircle2 className="mr-1 h-3 w-3" />
                                                Completed
                                            </Badge>
                                        ) : (
                                            <Badge variant="secondary" className="bg-yellow-50 text-yellow-700">
                                                <AlertTriangle className="mr-1 h-3 w-3" />
                                                Pending
                                            </Badge>
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right">{formatCurrency(audit.total_room_revenue)}</TableCell>
                                    <TableCell className="text-right">{formatCurrency(audit.total_tax)}</TableCell>
                                    <TableCell className="text-right">{audit.occupancy_percentage}%</TableCell>
                                    <TableCell className="text-right">{audit.no_shows_processed}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
