import { cva, type VariantProps } from "class-variance-authority";
import type * as React from "react";
import { cn } from "../../lib/utils";

const buttonVariants = cva("inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-800 disabled:pointer-events-none disabled:opacity-50", {
  variants: {
    variant: {
      default: "bg-[#0F1B15] text-white hover:bg-[#26352B]",
      lime: "bg-[#C6F24E] text-[#0F1B15] hover:bg-[#d5f776]",
      outline: "border border-[#E2E5DC] bg-white text-[#0F1B15] hover:bg-[#F5F6F1]",
      ghost: "text-[#0F1B15] hover:bg-[#E9ECE5]",
    },
    size: { default: "px-5", sm: "min-h-10 rounded-[12px] px-3", icon: "h-11 w-11 p-0" },
  },
  defaultVariants: { variant: "default", size: "default" },
});

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}
