'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getBlocks,
    createBlock,
    releaseBlock,
    RoomBlock,
    RoomBlockCreate,
} from '@/lib/api/blocks';

export function useBlocks(startDate: string, endDate: string, roomTypeId?: number) {
    return useQuery({
        queryKey: ['blocks', startDate, endDate, roomTypeId],
        queryFn: () => getBlocks(startDate, endDate, roomTypeId),
        enabled: !!startDate && !!endDate,
    });
}

export function useCreateBlock() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (block: RoomBlockCreate) => createBlock(block),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['blocks'] });
            queryClient.invalidateQueries({ queryKey: ['calendar'] });
        },
    });
}

export function useReleaseBlock() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (blockId: number) => releaseBlock(blockId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['blocks'] });
            queryClient.invalidateQueries({ queryKey: ['calendar'] });
        },
    });
}
