interface EmptyStateProps {
  readonly title: string;
  readonly description: string;
  readonly hint?: string;
}

export function EmptyState({ title, description, hint }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon" aria-hidden="true">
        ◇
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {hint && <p className="empty-state-hint">{hint}</p>}
    </div>
  );
}
