import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customerApi } from '@/lib/api/customers';
import { CustomerCreate, CustomerUpdate } from '@/types/customer';
import { toast } from 'sonner';
import { getMockCustomers, getMockCustomerById, mockBookings } from '@/lib/mock-data';

export function useCustomers(page = 1, limit = 10, search?: string) {
    return useQuery({
        queryKey: ['customers', page, limit, search],
        queryFn: async () => {
            try {
                return await customerApi.getAll(page, limit, search);
            } catch (error) {
                console.warn('API unavailable, using mock data');
                return getMockCustomers(page, limit);
            }
        },
    });
}

export function useCustomer(id: number) {
    return useQuery({
        queryKey: ['customer', id],
        queryFn: async () => {
            try {
                return await customerApi.getById(id);
            } catch (error) {
                console.warn('API unavailable, using mock data');
                return getMockCustomerById(id);
            }
        },
        enabled: !!id,
    });
}

export function useCustomerHistory(id: number) {
    return useQuery({
        queryKey: ['customer-history', id],
        queryFn: async () => {
            try {
                return await customerApi.getHistory(id);
            } catch (error) {
                console.warn('API unavailable, using mock data');
                // Filter mock bookings by customer_id
                return mockBookings.filter(b => b.customer_id === id);
            }
        },
        enabled: !!id,
    });
}

export function useCreateCustomer() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: customerApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['customers'] });
            toast.success('Customer created successfully');
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to create customer');
        },
    });
}

export function useUpdateCustomer() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: CustomerUpdate }) =>
            customerApi.update(id, data),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['customers'] });
            queryClient.invalidateQueries({ queryKey: ['customer', data.id] });
            toast.success('Customer updated successfully');
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to update customer');
        },
    });
}
