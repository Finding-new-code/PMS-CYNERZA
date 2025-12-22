'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { RoomType } from '@/types/room';
import { toast } from 'sonner';

const roomTypeSchema = z.object({
    name: z.string().min(1, 'Name is required').max(100),
    description: z.string().max(500).optional(),
    base_price: z.coerce.number().positive('Price must be positive'),
    capacity_adults: z.coerce.number().min(1, 'At least 1 adult').max(10),
    capacity_children: z.coerce.number().min(0).max(10),
    total_inventory: z.coerce.number().min(1, 'At least 1 room required'),
});

type RoomTypeFormValues = z.infer<typeof roomTypeSchema>;

interface RoomTypeFormProps {
    initialData?: RoomType;
    roomTypeId?: number;
}

export function RoomTypeForm({ initialData, roomTypeId }: RoomTypeFormProps) {
    const router = useRouter();
    const isEditing = !!initialData;

    const form = useForm<RoomTypeFormValues>({
        resolver: zodResolver(roomTypeSchema) as any,
        defaultValues: {
            name: initialData?.name || '',
            description: initialData?.description || '',
            base_price: initialData?.base_price || 100,
            capacity_adults: initialData?.capacity_adults || 2,
            capacity_children: initialData?.capacity_children || 0,
            total_inventory: initialData?.total_inventory || 10,
        },
    });

    const onSubmit = async (data: RoomTypeFormValues) => {
        try {
            // In demo mode, just show success message
            console.log('Room type data:', data);
            toast.success(isEditing ? 'Room type updated successfully' : 'Room type created successfully');
            router.push('/rooms');
        } catch (error) {
            toast.error('Failed to save room type');
        }
    };

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                <div className="grid gap-6 md:grid-cols-2">
                    <FormField
                        control={form.control}
                        name="name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Room Type Name</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Deluxe Suite" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="base_price"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Base Price (per night)</FormLabel>
                                <FormControl>
                                    <Input type="number" step="0.01" placeholder="150.00" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Description</FormLabel>
                            <FormControl>
                                <Textarea
                                    placeholder="Describe the room type, amenities, etc."
                                    className="resize-none"
                                    {...field}
                                />
                            </FormControl>
                            <FormDescription>
                                Optional description for guests.
                            </FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="grid gap-6 md:grid-cols-3">
                    <FormField
                        control={form.control}
                        name="capacity_adults"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Max Adults</FormLabel>
                                <FormControl>
                                    <Input type="number" min="1" max="10" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="capacity_children"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Max Children</FormLabel>
                                <FormControl>
                                    <Input type="number" min="0" max="10" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="total_inventory"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Total Rooms</FormLabel>
                                <FormControl>
                                    <Input type="number" min="1" {...field} />
                                </FormControl>
                                <FormDescription>
                                    Number of rooms of this type.
                                </FormDescription>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="flex gap-4">
                    <Button type="submit" disabled={form.formState.isSubmitting}>
                        {form.formState.isSubmitting && (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        {isEditing ? 'Update Room Type' : 'Create Room Type'}
                    </Button>
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => router.push('/rooms')}
                    >
                        Cancel
                    </Button>
                </div>
            </form>
        </Form>
    );
}
