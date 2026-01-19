
import { Menu } from "lucide-react";

interface NavProps {
    onMenuClick: () => void;
}

export function Nav({ onMenuClick }: NavProps) {
    return (
        <header className="sticky top-0 z-40 flex items-center justify-between px-4 h-16 bg-white border-b border-slate-200 lg:hidden">
            <div className="flex items-center gap-2">
                {/* Simple Logo for mobile top bar */}
                <img src="/logo.webp" alt="ResolveAI Logo" className="h-8 w-8 rounded-lg object-contain" />
                <span className="text-lg font-bold text-slate-900">ResolveAI</span>
            </div>
            <button
                onClick={onMenuClick}
                className="p-2 -mr-2 text-slate-500 hover:bg-slate-100 rounded-lg transition-colors"
            >
                <Menu className="h-6 w-6" />
                <span className="sr-only">Open menu</span>
            </button>
        </header>
    );
}
