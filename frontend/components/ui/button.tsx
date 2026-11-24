import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type Variant = "default" | "outline" | "ghost";

const styles: Record<Variant, string> = {
  default: "bg-accent text-white hover:bg-accent/90",
  outline: "border border-line text-zinc-200 hover:bg-white/5",
  ghost: "text-zinc-300 hover:bg-white/5",
};

export function Button({
  className,
  variant = "default",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={cn(
        "inline-flex h-9 items-center justify-center gap-2 rounded-lg px-3 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 disabled:opacity-50",
        styles[variant],
        className,
      )}
      {...props}
    />
  );
}
