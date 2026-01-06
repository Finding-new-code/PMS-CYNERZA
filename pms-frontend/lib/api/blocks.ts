import { apiClient } from './client';

// Types
export interface RoomBlock {
    id: number;
    room_type_id: number;
    start_date: string;
    end_date: string;
    block_type: 'maintenance' | 'hold' | 'out_of_service';
    num_rooms: number;
    reason?: string;
    status: 'active' | 'released' | 'expired' | 'converted';
    release_date?: string;
}

export interface RoomBlockCreate {
    room_type_id: number;
    start_date: string;
    end_date: string;
    block_type: 'maintenance' | 'hold' | 'out_of_service';
    num_rooms: number;
    reason?: string;
    release_date?: string;
}

// API Functions
export async function getBlocks(
    startDate: string,
    endDate: string,
    roomTypeId?: number
): Promise<RoomBlock[]> {
    const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
    });
    if (roomTypeId) {
        params.append('room_type_id', roomTypeId.toString());
    }
    const { data } = await apiClient.get<RoomBlock[]>(`/blocks?${params}`);
    return data;
}

export async function createBlock(block: RoomBlockCreate): Promise<RoomBlock> {
    const { data } = await apiClient.post<RoomBlock>('/blocks', block);
    return data;
}

export async function releaseBlock(blockId: number): Promise<RoomBlock> {
    const { data } = await apiClient.post<RoomBlock>(`/blocks/${blockId}/release`);
    return data;
}

export async function triggerAutoRelease(): Promise<{ released_count: number }> {
    const { data } = await apiClient.post<{ released_count: number }>('/blocks/auto-release');
    return data;
}
