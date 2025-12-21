import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roomTypeService } from '../services/roomType';
import { bookingService } from '../services/booking';
import { useForm, useFieldArray } from 'react-hook-form';
import { Loader2, Plus, Trash2, ArrowLeft } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function NewBooking() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [error, setError] = useState<string | null>(null);

    const { data: roomTypes, isLoading: isLoadingRooms } = useQuery({
        queryKey: ['roomTypes'],
        queryFn: roomTypeService.getAll,
    });

    const form = useForm({
        defaultValues: {
            check_in: '',
            check_out: '',
            rooms: [{ room_type_id: '', quantity: 1 }],
            customer: {
                name: '',
                email: '',
                phone: ''
            },
            notes: '',
            amount_paid: 0
        }
    });

    const { fields, append, remove } = useFieldArray({
        control: form.control,
        name: "rooms"
    });

    const createMutation = useMutation({
        mutationFn: bookingService.createMultiRoom,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['bookings'] });
            navigate('/bookings');
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || "Failed to create booking");
        }
    });

    const onSubmit = (data: any) => {
        // Transform data types
        const payload = {
            ...data,
            rooms: data.rooms.map((r: any) => ({
                room_type_id: Number(r.room_type_id),
                quantity: Number(r.quantity)
            })),
            amount_paid: Number(data.amount_paid)
        };
        createMutation.mutate(payload);
    };

    if (isLoadingRooms) return <div className="flex justify-center p-8"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="max-w-4xl mx-auto">
            <Link to="/bookings" className="flex items-center text-gray-500 hover:text-gray-900 mb-6 w-fit">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Bookings
            </Link>

            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold text-gray-900">New Booking</h1>
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-md mb-6 border border-red-100">
                    {error}
                </div>
            )}

            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Dates & Customer Block */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-medium mb-4">Dates</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Check In</label>
                                <input type="date" {...form.register('check_in', { required: true })} className="w-full border rounded-md px-3 py-2" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Check Out</label>
                                <input type="date" {...form.register('check_out', { required: true })} className="w-full border rounded-md px-3 py-2" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-medium mb-4">Customer Info</h2>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                                <input {...form.register('customer.name', { required: true })} className="w-full border rounded-md px-3 py-2" placeholder="John Doe" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                    <input type="email" {...form.register('customer.email', { required: true })} className="w-full border rounded-md px-3 py-2" placeholder="john@example.com" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                                    <input {...form.register('customer.phone')} className="w-full border rounded-md px-3 py-2" placeholder="+1234567890" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Rooms Block */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-medium">Rooms</h2>
                        <button
                            type="button"
                            onClick={() => append({ room_type_id: '', quantity: 1 })}
                            className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded flex items-center gap-1"
                        >
                            <Plus className="h-3 w-3" /> Add Room
                        </button>
                    </div>

                    <div className="space-y-4">
                        {fields.map((field, index) => (
                            <div key={field.id} className="flex gap-4 items-end bg-gray-50 p-3 rounded-md">
                                <div className="flex-1">
                                    <label className="block text-xs font-medium text-gray-500 mb-1">Room Type</label>
                                    <div className="relative">
                                        <select
                                            {...form.register(`rooms.${index}.room_type_id` as const, { required: true })}
                                            className="w-full border rounded-md px-3 py-2 bg-white"
                                        >
                                            <option value="">Select Room Type</option>
                                            {roomTypes?.map(type => (
                                                <option key={type.id} value={type.id}>
                                                    {type.name} (${type.base_price}/night) - {type.total_rooms} total
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                                <div className="w-24">
                                    <label className="block text-xs font-medium text-gray-500 mb-1">Quantity</label>
                                    <input
                                        type="number"
                                        min="1"
                                        {...form.register(`rooms.${index}.quantity` as const, { required: true, min: 1 })}
                                        className="w-full border rounded-md px-3 py-2"
                                    />
                                </div>
                                {fields.length > 1 && (
                                    <button
                                        type="button"
                                        onClick={() => remove(index)}
                                        className="text-red-500 hover:bg-red-50 p-2 rounded"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Payment/Notes Block */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Payment Received ($)</label>
                            <input type="number" {...form.register('amount_paid')} className="w-full border rounded-md px-3 py-2" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                            <textarea {...form.register('notes')} className="w-full border rounded-md px-3 py-2 h-[42px]" />
                        </div>
                    </div>
                </div>

                <div className="flex justify-end pt-4">
                    <button
                        type="submit"
                        disabled={createMutation.isPending}
                        className="bg-primary text-primary-foreground px-8 py-3 rounded-md font-medium hover:bg-slate-800 disabled:opacity-50 flex items-center gap-2"
                    >
                        {createMutation.isPending && <Loader2 className="animate-spin h-4 w-4" />}
                        {createMutation.isPending ? "Creating Booking..." : "Create Booking"}
                    </button>
                </div>
            </form>
        </div>
    );
}
