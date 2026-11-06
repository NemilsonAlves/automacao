export const SYSTEM_ROLES = [
  "SUPER_ADMIN",
  "ADMIN",
  "FINANCEIRO",
  "SUPORTE",
  "GERENTE_TENANT",
  "OPERADOR",
  "VISUALIZADOR",
] as const;

export type SystemRole = (typeof SYSTEM_ROLES)[number];

export type PermissionAction =
  | "read"
  | "create"
  | "update"
  | "delete"
  | "publish"
  | "approve"
  | "export"
  | "manage";

export type Permission = `${string}:${PermissionAction}`;

export function isSystemRole(value: string): value is SystemRole {
  return (SYSTEM_ROLES as readonly string[]).includes(value);
}

/**
 * O enforcement real ocorre no backend. Este helper existe apenas para a
 * camada de apresentação e será alimentado pelo contexto de sessão na FASE 2.
 */
export function isPermissionGranted(
  granted: ReadonlySet<Permission>,
  required: Permission,
): boolean {
  return granted.has(required);
}
