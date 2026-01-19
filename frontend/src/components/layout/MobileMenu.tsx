import * as React from "react";
import { NavLink } from "react-router-dom";
import {
    LayoutDashboard,
    CreditCard,
    Map as MapIcon,
    TrendingUp,
    Settings,
    LogOut,
    X,
    PieChart
} from "lucide-react";
import { cn } from "../../utils/cn";
import { useAuth } from "../../hooks/useAuth";

const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "My Debts", href: "/debts", icon: CreditCard },
    { name: "My Plan", href: "/plan", icon: MapIcon },
    { name: "Insights", href: "/insights", icon: PieChart },
    { name: "Negotiate", href: "/negotiate", icon: TrendingUp },
    { name: "Settings", href: "/settings", icon: Settings },
];

interface MobileMenuProps {
    isOpen: boolean;
    onClose: () => void;
}

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
    const { user, logout } = useAuth();

    // Prevent scrolling when menu is open
    React.useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "unset";
        }
        return () => {
            document.body.style.overflow = "unset";
        };
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200"
                onClick={onClose}
            />

            {/* Panel */}
            <div className="fixed inset-y-0 left-0 w-full max-w-xs bg-white shadow-xl animate-in slide-in-from-left duration-200 flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                        <img src="/logo.webp" alt="ResolveAI Logo" className="h-8 w-8 rounded-lg object-contain" />
                        <span className="text-xl font-bold text-slate-900">ResolveAI</span>
                    </div>
                    <button
                        onClick={onClose}
                        className="rounded-full p-2 text-slate-400 hover:bg-slate-100 transition-colors"
                    >
                        <X className="h-6 w-6" />
                    </button>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.name}
                            to={item.href}
                            onClick={onClose}
                            className={({ isActive }) =>
                                cn(
                                    "flex items-center gap-3 px-3 py-3 rounded-lg text-base font-medium transition-colors",
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

                <div className="p-4 border-t border-slate-200 bg-slate-50">
                    <div className="flex items-center gap-3 px-2 mb-4">
                        <div className="h-10 w-10 rounded-full bg-white border border-slate-200 text-main flex items-center justify-center font-semibold shadow-sm">
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
                        onClick={() => {
                            logout();
                            onClose();
                        }}
                        className="flex w-full items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium text-red-600 bg-white border border-slate-200 hover:bg-red-50 hover:border-red-100 transition-colors shadow-sm"
                    >
                        <LogOut className="h-5 w-5" />
                        Sign Out
                    </button>
                </div>
            </div>
        </div>
    );
}
