import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roomApi } from '@/lib/api/rooms';
import { RoomTypeCreate } from '@/types/room';
import { toast } from 'sonner';
import { getMockRoomTypes, mockRoomTypes } from '@/lib/mock-data';

export function useRoomTypes() {
    return useQuery({
        queryKey: ['room-types'],
        queryFn: async () => {
            try {
                return await roomApi.getTypes();
            } catch (error) {
                console.warn('API unavailable, using mock data');
                return getMockRoomTypes();
            }
        },
    });
}

export function useRoomType(id: number) {
    return useQuery({
        queryKey: ['room-type', id],
        queryFn: async () => {
            try {
                return await roomApi.getTypeById(id);
            } catch (error) {
                console.warn('API unavailable, using mock data');
                return mockRoomTypes.find(rt => rt.id === id);
            }
        },
        enabled: !!id,
    });
}

// Mutations can be added later as needed
