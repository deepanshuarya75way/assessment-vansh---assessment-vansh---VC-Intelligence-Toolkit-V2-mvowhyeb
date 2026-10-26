import ReasoningLine from "@/components/ReasoningLine";

export default function LoadingReasoning({ steps }: { steps: string[] }) {
  return (
    <div className="mt-8 space-y-3 rounded-xl border border-border bg-white p-5">
      {steps.map((step, index) => (
        <ReasoningLine key={step} text={step} index={index} />
      ))}
    </div>
  );
}
