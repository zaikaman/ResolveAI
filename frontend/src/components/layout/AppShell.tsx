import * as React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Nav } from "./Nav";
import { MobileMenu } from "./MobileMenu";

export function AppShell() {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

    return (
        <div className="flex h-screen bg-slate-50 overflow-hidden">
            {/* Desktop Sidebar */}
            <div className="hidden lg:block lg:flex-shrink-0">
                <Sidebar className="w-64" />
            </div>

            <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
                {/* Mobile Nav */}
                <Nav onMenuClick={() => setIsMobileMenuOpen(true)} />

                {/* Mobile Menu Overlay */}
                <MobileMenu
                    isOpen={isMobileMenuOpen}
                    onClose={() => setIsMobileMenuOpen(false)}
                />

                {/* Main Content Area */}
                <main className="flex-1 overflow-y-auto focus:outline-none p-4 md:p-6 lg:p-8">
                    <div className="max-w-7xl mx-auto w-full">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
}
