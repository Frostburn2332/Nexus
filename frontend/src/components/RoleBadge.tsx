import type { UserRole } from "../types";

interface RoleBadgeProps {
  role: UserRole;
}

const styles: Record<UserRole, string> = {
  admin: "bg-purple-100 text-purple-800",
  manager: "bg-blue-100 text-blue-800",
  viewer: "bg-gray-100 text-gray-700",
};

const labels: Record<UserRole, string> = {
  admin: "Admin",
  manager: "Manager",
  viewer: "Viewer",
};

export default function RoleBadge({ role }: RoleBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[role]}`}
    >
      {labels[role]}
    </span>
  );
}
