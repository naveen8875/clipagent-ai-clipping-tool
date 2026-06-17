import { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface PlasticButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  text: string;
}

export function PlasticButton({
  text,
  className,
  type = "button",
  ...props
}: PlasticButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "relative inline-flex items-center justify-center rounded-full px-5 py-2 text-sm font-medium text-white transition-all duration-200",
        "active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60",
        className
      )}
      style={{
        background:
          "linear-gradient(to bottom, rgb(59, 130, 246), rgb(37, 99, 235))",
        boxShadow:
          "0 2px 8px 0 rgba(37, 99, 235, 0.35), 0 1.5px 0 0 rgba(255,255,255,0.25) inset, 0 -2px 8px 0 rgba(37, 99, 235, 0.5) inset",
      }}
      {...props}
    >
      <span className="relative z-10">{text}</span>
      <span
        className="pointer-events-none absolute left-1/2 top-0 z-20 h-2/5 w-[80%] -translate-x-1/2 rounded-t-full"
        style={{
          background:
            "linear-gradient(180deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0) 80%, transparent 100%)",
          filter: "blur(1.5px)",
        }}
      />
      <span
        className="pointer-events-none absolute inset-0 z-0 rounded-full"
        style={{
          boxShadow:
            "0 0 0 2px rgba(255,255,255,0.10) inset, 0 1.5px 0 0 rgba(255,255,255,0.18) inset, 0 -2px 8px 0 rgba(37, 99, 235, 0.18) inset",
        }}
      />
    </button>
  );
}
