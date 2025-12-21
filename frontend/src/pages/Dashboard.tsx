import { useQuery } from '@tanstack/react-query';
import { bookingService } from '../services/booking';
import { roomTypeService } from '../services/roomType';
import { Loader2 } from 'lucide-react';

export default function Dashboard() {
    const { data: bookings, isLoading: isLoadingBookings } = useQuery({
        queryKey: ['bookings'],
        queryFn: bookingService.getAll,
    });

    const { data: roomTypes, isLoading: isLoadingRooms } = useQuery({
        queryKey: ['roomTypes'],
        queryFn: roomTypeService.getAll,
    });

    if (isLoadingBookings || isLoadingRooms) {
        return <div className="flex justify-center p-8"><Loader2 className="animate-spin" /></div>;
    }

    const totalRevenue = bookings?.reduce((acc, curr) => acc + curr.total_amount, 0) || 0;
    const totalBookings = bookings?.length || 0;
    const totalRoomTypes = roomTypes?.length || 0;

    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium">Total Bookings</h3>
                    <p className="text-3xl font-bold mt-2">{totalBookings}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium">Room Types</h3>
                    <p className="text-3xl font-bold mt-2">{totalRoomTypes}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium">Total Revenue</h3>
                    <p className="text-3xl font-bold mt-2">${totalRevenue.toLocaleString()}</p>
                </div>
            </div>
        </div>
    );
}
