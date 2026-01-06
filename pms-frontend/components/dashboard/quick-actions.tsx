'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
    Plus,
    Calendar,
    UserPlus,
    BarChart3,
    ClipboardList
} from 'lucide-react';
import Link from 'next/link';

interface QuickAction {
    label: string;
    href: string;
    icon: React.ReactNode;
    description: string;
    variant?: 'default' | 'primary';
}

const quickActions: QuickAction[] = [
    {
        label: 'New Booking',
        href: '/bookings/new',
        icon: <Plus className="h-4 w-4" />,
        description: 'Create a reservation',
        variant: 'primary',
    },
    {
        label: 'Calendar',
        href: '/calendar',
        icon: <Calendar className="h-4 w-4" />,
        description: 'View availability',
    },
    {
        label: 'Add Guest',
        href: '/customers/new',
        icon: <UserPlus className="h-4 w-4" />,
        description: 'Register customer',
    },
    {
        label: 'Reports',
        href: '/reports',
        icon: <BarChart3 className="h-4 w-4" />,
        description: 'View analytics',
    },
];

export function QuickActions() {
    return (
        <Card>
            <CardContent className="p-4">
                <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-3">
                    Quick Actions
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {quickActions.map((action) => (
                        <Link key={action.label} href={action.href}>
                            <Button
                                variant={action.variant === 'primary' ? 'default' : 'outline'}
                                className={`w-full h-auto flex-col gap-1 py-3 ${action.variant === 'primary'
                                        ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                                        : ''
                                    }`}
                            >
                                {action.icon}
                                <span className="text-xs font-medium">{action.label}</span>
                            </Button>
                        </Link>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
