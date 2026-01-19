import * as React from "react";
import { CheckCircle2, AlertCircle, Info, XCircle, X } from "lucide-react";
import { cn } from "../../utils/cn";

export type ToastType = "success" | "error" | "info" | "warning";

export interface ToastProps {
    id: string;
    type: ToastType;
    title?: string;
    message: string;
    onDismiss: (id: string) => void;
}

export function Toast({ id, type, title, message, onDismiss }: ToastProps) {
    const icons = {
        success: <CheckCircle2 className="h-5 w-5 text-green-500" />,
        error: <XCircle className="h-5 w-5 text-red-500" />,
        info: <Info className="h-5 w-5 text-blue-500" />,
        warning: <AlertCircle className="h-5 w-5 text-yellow-500" />,
    };

    const bgColors = {
        success: "bg-green-50 border-green-200",
        error: "bg-red-50 border-red-200",
        info: "bg-blue-50 border-blue-200",
        warning: "bg-yellow-50 border-yellow-200",
    };

    return (
        <div
            className={cn(
                "flex w-full max-w-sm overflow-hidden rounded-lg border shadow-lg ring-1 ring-black/5 animate-in slide-in-from-right-full duration-300",
                bgColors[type]
            )}
            role="alert"
        >
            <div className="flex w-full p-4">
                <div className="flex-shrink-0">{icons[type]}</div>
                <div className="ml-3 w-0 flex-1 pt-0.5">
                    {title && (
                        <p className="text-sm font-medium text-slate-900 mb-1">{title}</p>
                    )}
                    <p className="text-sm text-slate-600">{message}</p>
                </div>
                <div className="ml-4 flex flex-shrink-0">
                    <button
                        type="button"
                        className="inline-flex rounded-md text-slate-400 hover:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        onClick={() => onDismiss(id)}
                    >
                        <span className="sr-only">Close</span>
                        <X className="h-5 w-5" aria-hidden="true" />
                    </button>
                </div>
            </div>
        </div>
    );
}

export function ToastContainer({ children }: { children: React.ReactNode }) {
    return (
        <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 w-full max-w-sm pointer-events-none">
            <div className="pointer-events-auto flex flex-col gap-3 w-full">
                {children}
            </div>
        </div>
    );
}
