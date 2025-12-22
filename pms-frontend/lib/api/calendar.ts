import { apiClient } from './client';
import { Booking } from '@/types/booking';

export interface CalendarAvailability {
    date: string;
    room_types: {
        id: number;
        name: string;
        total: number;
        available: number;
        booked: number;
    }[];
}

export const calendarApi = {
    getAvailability: async (startDate: string, endDate: string) => {
        const { data } = await apiClient.get<CalendarAvailability[]>('/calendar/availability', {
            params: { start_date: startDate, end_date: endDate },
        });
        return data;
    },

    getBookings: async (startDate: string, endDate: string) => {
        const { data } = await apiClient.get<Booking[]>('/calendar/bookings', {
            params: { start_date: startDate, end_date: endDate },
        });
        return data;
    },
};
