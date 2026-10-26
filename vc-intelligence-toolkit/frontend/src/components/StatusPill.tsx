type StatusPillProps = {
  label: string;
  tone?: "accent" | "muted" | "dark";
};

export default function StatusPill({ label, tone = "muted" }: StatusPillProps) {
  const dot =
    tone === "accent" ? "bg-terracotta" : tone === "dark" ? "bg-ink" : "bg-ink-secondary";

  return (
    <span className="inline-flex items-center gap-2 text-sm text-ink-secondary">
      <span className={["h-2 w-2 rounded-full", dot].join(" ")} />
      {label}
    </span>
  );
}
