import { useState } from "react"
import { LayoutDashboard, Calendar, BedDouble, Users, Layers, Menu, LogOut } from "lucide-react"
import { Link, Outlet, useLocation } from "react-router-dom"
import { cn } from "../lib/utils"
import { useAuth } from "../context/AuthContext"

export default function DashboardLayout() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true)
    const location = useLocation()
    const { user, logout } = useAuth()

    const navItems = [
        { name: "Dashboard", href: "/", icon: LayoutDashboard },
        { name: "Bookings", href: "/bookings", icon: Calendar },
        { name: "Rooms", href: "/rooms", icon: BedDouble },
        { name: "Inventory", href: "/inventory", icon: Layers },
        { name: "Customers", href: "/customers", icon: Users },
    ]

    return (
        <div className="min-h-screen bg-gray-50 flex font-sans text-gray-900">
            {/* Sidebar */}
            <aside
                className={cn(
                    "bg-white border-r border-gray-200 fixed lg:static inset-y-0 left-0 z-50 transition-all duration-300 ease-in-out",
                    isSidebarOpen ? "w-64" : "w-20 -translate-x-full lg:translate-x-0"
                )}
            >
                <div className="h-16 flex items-center justify-center border-b border-gray-200">
                    {isSidebarOpen ? <span className="text-xl font-bold text-primary">Hotel PMS</span> : <span className="text-xl font-bold text-primary">H</span>}
                </div>

                <nav className="p-4 space-y-2">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.href
                        return (
                            <Link
                                key={item.href}
                                to={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                                    isActive
                                        ? "bg-slate-900 text-white"
                                        : "text-gray-600 hover:bg-gray-100",
                                    !isSidebarOpen && "justify-center"
                                )}
                                title={!isSidebarOpen ? item.name : undefined}
                            >
                                <item.icon className="h-5 w-5" />
                                {isSidebarOpen && <span className="text-sm font-medium">{item.name}</span>}
                            </Link>
                        )
                    })}
                </nav>

                <div className="absolute bottom-4 left-0 right-0 p-4">
                    <button
                        onClick={logout}
                        className={cn("flex items-center gap-3 px-3 py-2 w-full text-red-600 hover:bg-red-50 rounded-md transition-colors", !isSidebarOpen && "justify-center")}
                    >
                        <LogOut className="h-5 w-5" />
                        {isSidebarOpen && <span className="text-sm font-medium">Logout</span>}
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="bg-white border-b border-gray-200 h-16 flex items-center px-6 justify-between sticky top-0 z-40">
                    <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 rounded-md hover:bg-gray-100 focus:outline-none">
                        <Menu className="h-6 w-6 text-gray-600" />
                    </button>
                    <div className="flex items-center gap-4">
                        <span className="text-sm font-medium text-gray-600 hidden md:block">{user?.email}</span>
                        <div className="h-8 w-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-medium shadow-sm uppercase">
                            {user?.email?.[0] || 'U'}
                        </div>
                    </div>
                </header>

                <main className="flex-1 p-6 overflow-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}
