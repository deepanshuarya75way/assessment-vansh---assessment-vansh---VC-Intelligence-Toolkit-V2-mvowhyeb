import { Check } from "lucide-react";

type ReasoningLineProps = {
  text: string;
  index: number;
};

export default function ReasoningLine({ text, index }: ReasoningLineProps) {
  return (
    <div
      className="reasoning-in flex items-center gap-3 opacity-0"
      style={{ animationDelay: `${index * 400}ms` }}
    >
      <span className="grid h-5 w-5 place-items-center rounded-full border border-terracotta text-terracotta">
        <Check className="h-3 w-3" />
      </span>
      <span className="text-sm text-ink-secondary">{text}</span>
    </div>
  );
}
