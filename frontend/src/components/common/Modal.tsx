import * as React from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { cn } from "../../utils/cn";

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    description?: string;
    children: React.ReactNode;
    footer?: React.ReactNode;
    size?: "sm" | "md" | "lg" | "xl" | "full";
}

export function Modal({
    isOpen,
    onClose,
    title,
    description,
    children,
    footer,
    size = "md",
}: ModalProps) {
    React.useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape") {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener("keydown", handleEscape);
            document.body.style.overflow = "hidden";
        }

        return () => {
            document.removeEventListener("keydown", handleEscape);
            document.body.style.overflow = "unset";
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const sizes = {
        sm: "max-w-sm",
        md: "max-w-lg",
        lg: "max-w-2xl",
        xl: "max-w-4xl",
        full: "max-w-full m-4",
    };

    return createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div
                className={cn(
                    "relative w-full bg-white rounded-xl shadow-2xl animate-in zoom-in-95 duration-200 flex flex-col max-h-[90vh]",
                    sizes[size]
                )}
                role="dialog"
                aria-modal="true"
            >
                <div className="flex items-center justify-between p-6 pb-2">
                    <div className="space-y-1">
                        {title && (
                            <h2 className="text-xl font-semibold leading-none text-slate-900">
                                {title}
                            </h2>
                        )}
                        {description && (
                            <p className="text-sm text-slate-500">{description}</p>
                        )}
                    </div>
                    <button
                        onClick={onClose}
                        className="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-500 transition-colors"
                    >
                        <X className="h-5 w-5" />
                        <span className="sr-only">Close</span>
                    </button>
                </div>

                <div className="p-6 overflow-y-auto custom-scrollbar">
                    {children}
                </div>

                {footer && (
                    <div className="flex items-center justify-end p-6 pt-2 bg-slate-50/50 rounded-b-xl border-t border-slate-100">
                        {footer}
                    </div>
                )}
            </div>
        </div>,
        document.body
    );
}
