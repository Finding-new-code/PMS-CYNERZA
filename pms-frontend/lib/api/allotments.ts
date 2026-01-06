import { apiClient } from './client';

// Types
export interface RoomAllocation {
    room_type_id: number;
    blocked_rooms: number;
}

export interface Allotment {
    id: number;
    name: string;
    status: 'lead' | 'tentative' | 'definite' | 'released' | 'cancelled';
    start_date: string;
    end_date: string;
    cutoff_date?: string;
    contact_name?: string;
    contact_email?: string;
    contact_phone?: string;
    group_rate?: number;
    notes?: string;
}

export interface AllotmentCreate {
    name: string;
    start_date: string;
    end_date: string;
    cutoff_date?: string;
    room_allocations: RoomAllocation[];
    contact_name?: string;
    contact_email?: string;
    contact_phone?: string;
    group_rate?: number;
    notes?: string;
}

export interface AllotmentPickupReport {
    allotment_id: number;
    name: string;
    status: string;
    start_date: string;
    end_date: string;
    total_room_nights_blocked: number;
    total_room_nights_picked: number;
    pickup_percentage: number;
    remaining_room_nights: number;
}

// API Functions
export async function getAllotments(status?: string): Promise<Allotment[]> {
    const params = status ? `?status=${status}` : '';
    const { data } = await apiClient.get<Allotment[]>(`/allotments${params}`);
    return data;
}

export async function getAllotment(id: number): Promise<Allotment> {
    const { data } = await apiClient.get<Allotment>(`/allotments/${id}`);
    return data;
}

export async function createAllotment(allotment: AllotmentCreate): Promise<Allotment> {
    const { data } = await apiClient.post<Allotment>('/allotments', allotment);
    return data;
}

export async function updateAllotmentStatus(
    id: number,
    status: Allotment['status']
): Promise<Allotment> {
    const { data } = await apiClient.patch<Allotment>(`/allotments/${id}/status`, { status });
    return data;
}

export async function getPickupReport(id: number): Promise<AllotmentPickupReport> {
    const { data } = await apiClient.get<AllotmentPickupReport>(`/allotments/${id}/pickup-report`);
    return data;
}
