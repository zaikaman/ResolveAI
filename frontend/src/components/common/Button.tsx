import * as React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "../../utils/cn";

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
    size?: "sm" | "md" | "lg" | "icon";
    isLoading?: boolean;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    (
        {
            className,
            variant = "primary",
            size = "md",
            isLoading = false,
            leftIcon,
            rightIcon,
            children,
            disabled,
            ...props
        },
        ref
    ) => {
        const variants = {
            primary: "bg-main text-white hover:bg-blue-700 shadow-sm shadow-shadowcolor/50 active:translate-y-0.5",
            secondary: "bg-main2 text-main hover:bg-blue-200 active:translate-y-0.5",
            outline: "border-2 border-main text-main bg-transparent hover:bg-main hover:text-white active:translate-y-0.5",
            ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
            danger: "bg-red-500 text-white hover:bg-red-600 shadow-sm shadow-red-200 active:translate-y-0.5",
        };

        const sizes = {
            sm: "h-8 px-3 text-xs",
            md: "h-10 px-4 py-2 text-sm",
            lg: "h-12 px-8 text-base",
            icon: "h-10 w-10 p-2",
        };

        return (
            <button
                className={cn(
                    "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-main focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
                    variants[variant],
                    sizes[size],
                    className
                )}
                ref={ref}
                disabled={disabled || isLoading}
                {...props}
            >
                {isLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : leftIcon ? (
                    <span className="mr-2">{leftIcon}</span>
                ) : null}
                {children}
                {!isLoading && rightIcon ? (
                    <span className="ml-2">{rightIcon}</span>
                ) : null}
            </button>
        );
    }
);
Button.displayName = "Button";

export { Button };
