import { ArrowRight } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type ActionButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  loading?: boolean;
};

export default function ActionButton({
  children,
  className = "",
  loading = false,
  disabled,
  ...props
}: ActionButtonProps) {
  const isDisabled = loading || disabled;

  return (
    <button
      className={[
        "group inline-flex items-center gap-3 rounded-full border border-ink bg-transparent px-5 py-3 text-sm font-medium text-ink transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] hover:border-ink disabled:cursor-not-allowed disabled:opacity-50",
        loading ? "cursor-wait" : "",
        className,
      ].join(" ")}
      aria-busy={loading}
      disabled={isDisabled}
      {...props}
    >
      <span className="relative h-[20px] overflow-hidden">
        <span className="block transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-translate-y-[20px]">
          {children}
        </span>
        <span className="absolute left-0 top-[20px] block transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-translate-y-[20px]">
          {children}
        </span>
      </span>
      <span className="grid h-8 w-8 place-items-center rounded-full border border-ink transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] group-hover:-rotate-45">
        {loading ? (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-ink border-r-transparent" />
        ) : (
          <ArrowRight className="h-4 w-4" />
        )}
      </span>
    </button>
  );
}
