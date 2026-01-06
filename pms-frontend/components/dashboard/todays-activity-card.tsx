'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useTodaysActivity } from '@/lib/hooks/use-dashboard';
import {
    ArrowDownToLine,
    ArrowUpFromLine,
    Users,
    AlertTriangle,
    XCircle,
    UserX
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatItemProps {
    label: string;
    value: number;
    subValue?: string;
    icon: React.ReactNode;
    variant?: 'default' | 'success' | 'warning' | 'danger';
}

function StatItem({ label, value, subValue, icon, variant = 'default' }: StatItemProps) {
    const variantStyles = {
        default: 'text-zinc-700 dark:text-zinc-300',
        success: 'text-emerald-600 dark:text-emerald-400',
        warning: 'text-amber-600 dark:text-amber-400',
        danger: 'text-red-600 dark:text-red-400',
    };

    return (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800/50">
            <div className={cn("p-2 rounded-md bg-white dark:bg-zinc-800 shadow-sm", variantStyles[variant])}>
                {icon}
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-xs text-zinc-500 dark:text-zinc-400 truncate">{label}</p>
                <div className="flex items-baseline gap-1.5">
                    <span className={cn("text-xl font-bold", variantStyles[variant])}>{value}</span>
                    {subValue && (
                        <span className="text-xs text-zinc-400 dark:text-zinc-500">{subValue}</span>
                    )}
                </div>
            </div>
        </div>
    );
}

export function TodaysActivityCard() {
    const { data, isLoading, error } = useTodaysActivity();

    if (error) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Today's Activity</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-red-500 text-sm">Failed to load activity data</div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    Today's Activity
                </CardTitle>
            </CardHeader>
            <CardContent>
                {isLoading ? (
                    <div className="grid grid-cols-2 gap-3">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <Skeleton key={i} className="h-20" />
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-3">
                        {/* Arrivals */}
                        <StatItem
                            label="Arrivals"
                            value={data?.arrivals_expected || 0}
                            subValue={`${data?.arrivals_checked_in || 0} in`}
                            icon={<ArrowDownToLine className="h-4 w-4" />}
                            variant="success"
                        />

                        {/* Departures */}
                        <StatItem
                            label="Departures"
                            value={data?.departures_expected || 0}
                            subValue={`${data?.departures_checked_out || 0} out`}
                            icon={<ArrowUpFromLine className="h-4 w-4" />}
                            variant="default"
                        />

                        {/* In-House */}
                        <StatItem
                            label="In-House"
                            value={data?.in_house_guests || 0}
                            icon={<Users className="h-4 w-4" />}
                            variant="default"
                        />

                        {/* Overbookings */}
                        <StatItem
                            label="Overbookings"
                            value={data?.overbookings || 0}
                            icon={<AlertTriangle className="h-4 w-4" />}
                            variant={(data?.overbookings || 0) > 0 ? 'danger' : 'default'}
                        />

                        {/* Cancellations */}
                        <StatItem
                            label="Cancellations"
                            value={data?.cancellations_today || 0}
                            icon={<XCircle className="h-4 w-4" />}
                            variant={(data?.cancellations_today || 0) > 0 ? 'warning' : 'default'}
                        />

                        {/* No-Shows */}
                        <StatItem
                            label="No-Shows"
                            value={data?.no_shows || 0}
                            icon={<UserX className="h-4 w-4" />}
                            variant={(data?.no_shows || 0) > 0 ? 'danger' : 'default'}
                        />
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
