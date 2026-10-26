import type { ReactNode } from "react";

export default function PageShell({ children }: { children: ReactNode }) {
  return <main className="mx-auto max-w-[1200px] px-6 py-14 md:py-20">{children}</main>;
}
