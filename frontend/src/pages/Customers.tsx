import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { customerService } from '../services/customer';
import { Loader2, Search, User, Phone, Mail, MapPin } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '../lib/utils';

export default function Customers() {
    const [search, setSearch] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');

    // Simple debounce for search
    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setSearch(value);
        const timeoutId = setTimeout(() => setDebouncedSearch(value), 500);
        return () => clearTimeout(timeoutId);
    };

    const { data: customers, isLoading, error } = useQuery({
        queryKey: ['customers', debouncedSearch],
        queryFn: () => customerService.getAll({ search: debouncedSearch }),
    });

    if (isLoading && !customers) return <div className="flex justify-center p-8"><Loader2 className="animate-spin" /></div>;
    if (error) return <div className="text-red-500 p-8">Error loading customers</div>;

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
                <p className="text-gray-500">Manage your guest database</p>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                    type="text"
                    placeholder="Search customers by name or email..."
                    className="w-full md:w-96 pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    value={search}
                    onChange={handleSearch}
                />
            </div>

            <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact Info</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bookings</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Balance Due</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {customers?.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-8 text-center text-gray-500">No customers found</td>
                            </tr>
                        ) : (
                            customers?.map((customer) => (
                                <tr key={customer.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="h-10 w-10 flex-shrink-0 bg-gray-100 rounded-full flex items-center justify-center text-gray-500">
                                                <User className="h-5 w-5" />
                                            </div>
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                                                <div className="text-sm text-gray-500">ID: #{customer.id}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-sm text-gray-500 flex flex-col gap-1">
                                            {customer.email && <div className="flex items-center gap-1"><Mail className="h-3 w-3" /> {customer.email}</div>}
                                            {customer.phone && <div className="flex items-center gap-1"><Phone className="h-3 w-3" /> {customer.phone}</div>}
                                            {customer.address && <div className="flex items-center gap-1"><MapPin className="h-3 w-3" /> {customer.address}</div>}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {customer.booking_count} bookings
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={cn(
                                            "px-2 inline-flex text-xs leading-5 font-semibold rounded-full",
                                            customer.total_balance_due > 0 ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"
                                        )}>
                                            ${customer.total_balance_due}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {format(new Date(customer.created_at), 'MMM dd, yyyy')}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
