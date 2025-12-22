'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { bookingSchema, BookingFormValues } from '@/lib/validations/booking';
import { useCreateBooking, useModifyBooking } from '@/lib/hooks/use-bookings';
import { useCustomers } from '@/lib/hooks/use-customers';
import { useRoomTypes } from '@/lib/hooks/use-rooms';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { Booking } from '@/types/booking';
import { format } from 'date-fns';

interface BookingFormProps {
    initialData?: Booking;
    bookingId?: number;
}

export function BookingForm({ initialData, bookingId }: BookingFormProps) {
    const router = useRouter();
    const createBooking = useCreateBooking();
    const modifyBooking = useModifyBooking();

    // Fetch data for dropdowns
    const { data: customersData, isLoading: isLoadingCustomers } = useCustomers(1, 100); // Fetch first 100 for now
    const { data: roomTypesData, isLoading: isLoadingRoomTypes } = useRoomTypes();

    // Normalize data access for both API and mock data formats
    const customers = (customersData as any)?.items || (customersData as any)?.data || customersData || [];
    const roomTypes = Array.isArray(roomTypesData) ? roomTypesData : (roomTypesData as any)?.data || [];

    const form = useForm<BookingFormValues>({
        resolver: zodResolver(bookingSchema) as any,
        defaultValues: {
            customer_id: initialData?.customer_id?.toString() || '',
            room_type_id: initialData?.room_type_id?.toString() || '',
            check_in: initialData?.check_in ? format(new Date(initialData.check_in), 'yyyy-MM-dd') : '',
            check_out: initialData?.check_out ? format(new Date(initialData.check_out), 'yyyy-MM-dd') : '',
            num_adults: initialData?.num_adults || 1,
            num_children: initialData?.num_children || 0,
            num_rooms: initialData?.num_rooms || 1,
            notes: initialData?.notes || '',
        },
    });

    async function onSubmit(data: BookingFormValues) {
        try {
            if (initialData && bookingId) {
                await modifyBooking.mutateAsync({
                    id: bookingId,
                    data: {
                        room_type_id: parseInt(data.room_type_id),
                        check_in: new Date(data.check_in),
                        check_out: new Date(data.check_out),
                        num_adults: data.num_adults,
                        num_children: data.num_children,
                        num_rooms: data.num_rooms,
                        notes: data.notes,
                        // Customer cannot be changed in simple edit usually, or we pass it if needed.
                        // For now assuming customer change is allowed but backend handle it.
                        // Actually Types usually expect customer_id.
                        customer_id: parseInt(data.customer_id),
                    },
                });
            } else {
                await createBooking.mutateAsync({
                    customer_id: parseInt(data.customer_id),
                    room_type_id: parseInt(data.room_type_id),
                    check_in: new Date(data.check_in),
                    check_out: new Date(data.check_out),
                    num_adults: data.num_adults,
                    num_children: data.num_children,
                    num_rooms: data.num_rooms,
                    notes: data.notes,
                });
            }
            router.push('/bookings');
        } catch (error) {
            // Error handled by mutation
        }
    }

    const isLoading = createBooking.isPending || modifyBooking.isPending || isLoadingCustomers || isLoadingRoomTypes;

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">

                    <FormField
                        control={form.control}
                        name="customer_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Customer</FormLabel>
                                <FormControl>
                                    <select
                                        className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        {...field}
                                    >
                                        <option value="">Select a customer</option>
                                        {customers.map((customer: any) => (
                                            <option key={customer.id} value={customer.id}>
                                                {customer.full_name} ({customer.email})
                                            </option>
                                        ))}
                                    </select>
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="room_type_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Room Type</FormLabel>
                                <FormControl>
                                    <select
                                        className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        {...field}
                                    >
                                        <option value="">Select a room type</option>
                                        {roomTypes?.map((type: any) => (
                                            <option key={type.id} value={type.id}>
                                                {type.name} - ${type.base_price}/night
                                            </option>
                                        ))}
                                    </select>
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="check_in"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Check In</FormLabel>
                                <FormControl>
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="check_out"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Check Out</FormLabel>
                                <FormControl>
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="num_adults"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Adults</FormLabel>
                                <FormControl>
                                    <Input type="number" min="1" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="num_children"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Children</FormLabel>
                                <FormControl>
                                    <Input type="number" min="0" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="num_rooms"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Number of Rooms</FormLabel>
                                <FormControl>
                                    <Input type="number" min="1" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="notes"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Notes</FormLabel>
                            <FormControl>
                                <Input className="h-20" placeholder="Special requests..." {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex justify-end gap-4">
                    <Button variant="outline" type="button" onClick={() => router.back()}>
                        Cancel
                    </Button>
                    <Button type="submit" disabled={isLoading}>
                        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {initialData ? 'Update Booking' : 'Create Booking'}
                    </Button>
                </div>
            </form>
        </Form>
    );
}
