import { apiClient } from './client';

// Types for Housekeeping API
export type RoomStatus = 'clean' | 'dirty' | 'inspected' | 'out_of_service';
export type OccupancyStatus = 'vacant' | 'occupied' | 'checkout' | 'arrival';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface Room {
    id: number;
    room_number: string;
    room_type_id: number;
    room_type_name: string;
    floor: number;
    status: RoomStatus;
    occupancy_status: OccupancyStatus;
    assigned_to?: number;
    assigned_to_name?: string;
    notes?: string;
}

export interface HousekeepingTask {
    id: number;
    room_id: number;
    room_number: string;
    task_type: string;
    description?: string;
    scheduled_date: string;
    status: TaskStatus;
    assigned_to?: number;
    assigned_to_name?: string;
    completed_at?: string;
    completed_by?: number;
    notes?: string;
}

export interface HousekeepingSummary {
    total_rooms: number;
    clean_rooms: number;
    dirty_rooms: number;
    inspected_rooms: number;
    out_of_service: number;
    pending_tasks: number;
    completed_tasks_today: number;
}

export interface RoomStatusUpdate {
    status: RoomStatus;
    notes?: string;
}

export interface TaskCreate {
    room_id: number;
    task_type: string;
    description?: string;
    scheduled_date: string;
    assigned_to?: number;
}

// Housekeeping API functions
export const housekeepingApi = {
    // Rooms
    listRooms: async (filters?: { status?: RoomStatus; occupancy?: OccupancyStatus; floor?: number }) => {
        const { data } = await apiClient.get<Room[]>('/housekeeping/rooms', { params: filters });
        return data;
    },

    getRoom: async (roomId: number) => {
        const { data } = await apiClient.get<Room>(`/housekeeping/rooms/${roomId}`);
        return data;
    },

    updateRoomStatus: async (roomId: number, update: RoomStatusUpdate) => {
        const { data } = await apiClient.put<Room>(`/housekeeping/rooms/${roomId}/status`, update);
        return data;
    },

    bulkUpdateStatus: async (roomIds: number[], status: RoomStatus) => {
        const { data } = await apiClient.put<{ updated: number }>('/housekeeping/rooms/bulk-status', {
            room_ids: roomIds,
            status,
        });
        return data;
    },

    // Tasks
    listTasks: async (filters?: { status?: TaskStatus; assigned_to?: number; task_date?: string }) => {
        const { data } = await apiClient.get<HousekeepingTask[]>('/housekeeping/tasks', { params: filters });
        return data;
    },

    createTask: async (task: TaskCreate) => {
        const { data } = await apiClient.post<HousekeepingTask>('/housekeeping/tasks', task);
        return data;
    },

    completeTask: async (taskId: number, notes?: string) => {
        const { data } = await apiClient.post<HousekeepingTask>(`/housekeeping/tasks/${taskId}/complete`, { notes });
        return data;
    },

    // Summary
    getSummary: async () => {
        const { data } = await apiClient.get<HousekeepingSummary>('/housekeeping/summary');
        return data;
    },
};
