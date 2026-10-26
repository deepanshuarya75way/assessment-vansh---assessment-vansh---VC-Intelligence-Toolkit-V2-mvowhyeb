import type { ReactNode } from "react";

type ReportCardProps = {
  children: ReactNode;
  className?: string;
};

export default function ReportCard({ children, className = "" }: ReportCardProps) {
  return (
    <article
      className={[
        "group relative rounded-xl border border-border bg-white p-6 transition duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] hover:shadow-md",
        className,
      ].join(" ")}
    >
      {children}
      <button
        type="button"
        className="absolute bottom-4 right-4 h-9 w-9 overflow-hidden rounded-full border border-border bg-white text-xs text-ink-secondary transition-all duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] hover:w-[140px] hover:text-ink"
      >
        <span className="block whitespace-nowrap px-3">View</span>
      </button>
    </article>
  );
}
