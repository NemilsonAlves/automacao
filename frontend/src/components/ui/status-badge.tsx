export type StatusTone = "neutral" | "positive" | "warning" | "info";

interface StatusBadgeProps {
  readonly children: React.ReactNode;
  readonly tone?: StatusTone;
}

export function StatusBadge({ children, tone = "neutral" }: StatusBadgeProps) {
  return <span className={`status-badge status-badge--${tone}`}>{children}</span>;
}
