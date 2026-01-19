import { NavLink } from "react-router-dom";
import {
    LayoutDashboard,
    CreditCard,
    Map as MapIcon,
    TrendingUp,
    Settings,
    LogOut,
    PieChart
} from "lucide-react";
import { cn } from "../../utils/cn";
import { useAuth } from "../../hooks/useAuth";

const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "My Debts", href: "/debts", icon: CreditCard },
    { name: "My Plan", href: "/plan", icon: MapIcon },
    { name: "Insights", href: "/insights", icon: PieChart },
    { name: "Negotiate", href: "/negotiate", icon: TrendingUp }, // Or maybe Handshake?
    { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar({ className }: { className?: string }) {
    // Mock auth for now if useAuth isn't fully ready or mock it
    // Assuming useAuth hooks returns user and signOut
    const { user, logout } = useAuth();

    return (
        <aside className={cn("flex flex-col h-full bg-white border-r border-slate-200 w-64", className)}>
            <div className="p-6">
                <div className="flex items-center gap-2">
                    {/* Logo could be here */}
                    <img src="/logo.webp" alt="ResolveAI Logo" className="h-8 w-8 rounded-lg object-contain" />
                    <span className="text-xl font-bold text-slate-900">ResolveAI</span>
                </div>
            </div>

            <nav className="flex-1 px-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.name}
                        to={item.href}
                        className={({ isActive }) =>
                            cn(
                                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-main3 text-main"
                                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                            )
                        }
                    >
                        <item.icon className="h-5 w-5" />
                        {item.name}
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-200">
                <div className="flex items-center gap-3 px-2 mb-3">
                    <div className="h-9 w-9 rounded-full bg-main2 text-main flex items-center justify-center font-semibold">
                        {user?.email?.[0]?.toUpperCase() || "U"}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900 truncate">
                            {user?.full_name || "User"}
                        </p>
                        <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                    </div>
                </div>
                <button
                    onClick={() => logout()}
                    className="flex w-full items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                    <LogOut className="h-5 w-5" />
                    Sign Out
                </button>
            </div>
        </aside>
    );
}
