type StepBadgeProps = {
  number: number;
  label: string;
};

export default function StepBadge({ number, label }: StepBadgeProps) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-border bg-white px-3 py-2 text-sm text-ink">
      <span className="grid h-7 w-7 place-items-center rounded-full bg-gray-900 text-xs font-semibold text-white">
        {number}
      </span>
      <span>{label}</span>
    </div>
  );
}
