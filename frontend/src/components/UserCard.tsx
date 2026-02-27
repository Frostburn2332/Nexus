import type { User, UserRole } from "../types";
import RoleBadge from "./RoleBadge";

interface UserCardProps {
  user: User;
  currentUserRole: UserRole;
  onChangeRole?: (user: User) => void;
  onDelete?: (user: User) => void;
}

export default function UserCard({
  user,
  currentUserRole,
  onChangeRole,
  onDelete,
}: UserCardProps) {
  const canManage = currentUserRole === "admin" || currentUserRole === "manager";
  const canDelete = currentUserRole === "admin";

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-gray-200 bg-white px-5 py-4 shadow-sm transition hover:shadow-md sm:flex-row sm:items-center sm:justify-between">
      {/* Avatar + info */}
      <div className="flex items-center gap-4">
        {user.profile_picture ? (
          <img
            src={user.profile_picture}
            alt={user.name}
            className="h-10 w-10 shrink-0 rounded-full object-cover"
          />
        ) : (
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
            {user.name.charAt(0).toUpperCase()}
          </div>
        )}
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-gray-900">{user.name}</p>
          <p className="truncate text-xs text-gray-500">{user.email}</p>
        </div>
      </div>

      {/* Badges + actions */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        <RoleBadge role={user.role} />

        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            user.status === "active"
              ? "bg-green-100 text-green-700"
              : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {user.status === "active" ? "Active" : "Pending"}
        </span>

        {canManage && (
          <button
            onClick={() => onChangeRole?.(user)}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 transition hover:bg-gray-50 active:scale-95"
          >
            Edit role
          </button>
        )}

        {canDelete && (
          <button
            onClick={() => onDelete?.(user)}
            className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-50 active:scale-95"
          >
            Remove
          </button>
        )}
      </div>
    </div>
  );
}
