import Link from "next/link";

interface BrandProps {
  readonly compact?: boolean;
}

export function Brand({ compact = false }: BrandProps) {
  return (
    <Link className="brand" href="/admin" aria-label="AgencIA NTM — início">
      <span className="brand-mark" aria-hidden="true">
        A
      </span>
      {!compact && (
        <span className="brand-text">
          <span className="brand-name">AgencIA NTM</span>
          <span className="brand-tagline">Neural Tech minds</span>
        </span>
      )}
    </Link>
  );
}
