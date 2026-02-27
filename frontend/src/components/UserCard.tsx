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
    <div className="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-5 py-4 shadow-sm transition hover:shadow-md">
      {/* Avatar + info */}
      <div className="flex items-center gap-4">
        {user.profile_picture ? (
          <img
            src={user.profile_picture}
            alt={user.name}
            className="h-10 w-10 rounded-full object-cover"
          />
        ) : (
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
            {user.name.charAt(0).toUpperCase()}
          </div>
        )}
        <div>
          <p className="text-sm font-medium text-gray-900">{user.name}</p>
          <p className="text-xs text-gray-500">{user.email}</p>
        </div>
      </div>

      {/* Role + status + actions */}
      <div className="flex items-center gap-3">
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
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-gray-600 border border-gray-200 hover:bg-gray-50 transition"
          >
            Edit role
          </button>
        )}

        {canDelete && (
          <button
            onClick={() => onDelete?.(user)}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 hover:bg-red-50 transition"
          >
            Remove
          </button>
        )}
      </div>
    </div>
  );
}
