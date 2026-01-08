import { apiClient } from './client';

// Types for Inventory API
export interface InventoryRecord {
    id: number;
    room_type_id: number;
    room_type_name: string | null;
    date: string;
    available_rooms: number;
    price: number;
}

export interface DateRangeAvailability {
    room_type_id: number;
    room_type_name: string;
    total_inventory: number;
    min_available: number;
    max_available: number;
    dates_with_low_availability: number;
}

export interface InventoryUpdate {
    available_rooms?: number;
    price?: number;
}

// Inventory API functions
export const inventoryApi = {
    getAvailability: async (startDate: string, endDate: string, roomTypeId?: number) => {
        const params: Record<string, string | number> = { start: startDate, end: endDate };
        if (roomTypeId) params.room_type_id = roomTypeId;

        const { data } = await apiClient.get<DateRangeAvailability[]>('/inventory', { params });
        return data;
    },

    getDetailed: async (startDate: string, endDate: string, roomTypeId?: number) => {
        const params: Record<string, string | number> = { start: startDate, end: endDate };
        if (roomTypeId) params.room_type_id = roomTypeId;

        const { data } = await apiClient.get<InventoryRecord[]>('/inventory/detailed', { params });
        return data;
    },

    update: async (inventoryId: number, updates: InventoryUpdate) => {
        const { data } = await apiClient.put<InventoryRecord>(`/inventory/${inventoryId}`, updates);
        return data;
    },

    regenerate: async (roomTypeId: number, daysAhead: number = 90) => {
        const { data } = await apiClient.post<{ message: string }>(
            `/inventory/generate/${roomTypeId}`,
            null,
            { params: { days_ahead: daysAhead } }
        );
        return data;
    },
};
