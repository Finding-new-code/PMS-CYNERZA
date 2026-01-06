'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getAllotments,
    getAllotment,
    createAllotment,
    updateAllotmentStatus,
    getPickupReport,
    Allotment,
    AllotmentCreate,
} from '@/lib/api/allotments';

export function useAllotments(status?: string) {
    return useQuery({
        queryKey: ['allotments', status],
        queryFn: () => getAllotments(status),
    });
}

export function useAllotment(id: number) {
    return useQuery({
        queryKey: ['allotment', id],
        queryFn: () => getAllotment(id),
        enabled: !!id,
    });
}

export function useCreateAllotment() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (allotment: AllotmentCreate) => createAllotment(allotment),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['allotments'] });
        },
    });
}

export function useUpdateAllotmentStatus() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, status }: { id: number; status: Allotment['status'] }) =>
            updateAllotmentStatus(id, status),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['allotments'] });
            queryClient.invalidateQueries({ queryKey: ['allotment', variables.id] });
        },
    });
}

export function usePickupReport(id: number) {
    return useQuery({
        queryKey: ['allotment-pickup', id],
        queryFn: () => getPickupReport(id),
        enabled: !!id,
    });
}
