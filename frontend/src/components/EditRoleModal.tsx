import { useState } from "react";
import { usersApi } from "../api/client";
import type { User, UserRole } from "../types";
import RoleBadge from "./RoleBadge";

interface EditRoleModalProps {
  user: User;
  onClose: () => void;
  onSuccess: (updated: User) => void;
}

const ROLE_OPTIONS: { value: UserRole; label: string; description: string }[] = [
  { value: "viewer", label: "Viewer", description: "Read-only access to team data." },
  { value: "manager", label: "Manager", description: "Can invite members and manage roles." },
  { value: "admin", label: "Admin", description: "Full access including deleting members." },
];

export default function EditRoleModal({ user, onClose, onSuccess }: EditRoleModalProps) {
  const [selectedRole, setSelectedRole] = useState<UserRole>(user.role);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const hasChanged = selectedRole !== user.role;

  const handleSave = async () => {
    if (!hasChanged) return;
    setIsLoading(true);
    setError("");
    try {
      const { data } = await usersApi.updateRole(user.id, selectedRole);
      onSuccess(data);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? "Failed to update role. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Edit role</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition"
          >
            ✕
          </button>
        </div>

        {/* User info */}
        <div className="mb-5 flex items-center gap-3 rounded-lg bg-gray-50 px-4 py-3">
          {user.profile_picture ? (
            <img
              src={user.profile_picture}
              alt={user.name}
              className="h-9 w-9 rounded-full object-cover"
            />
          ) : (
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
              {user.name.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <p className="text-sm font-medium text-gray-900">{user.name}</p>
            <p className="text-xs text-gray-500">{user.email}</p>
          </div>
          <div className="ml-auto">
            <RoleBadge role={user.role} />
          </div>
        </div>

        {/* Role options */}
        <div className="space-y-2 mb-5">
          {ROLE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setSelectedRole(opt.value)}
              className={`w-full rounded-lg border px-4 py-3 text-left transition ${
                selectedRole === opt.value
                  ? "border-indigo-500 bg-indigo-50"
                  : "border-gray-200 hover:bg-gray-50"
              }`}
            >
              <p className={`text-sm font-medium ${selectedRole === opt.value ? "text-indigo-700" : "text-gray-800"}`}>
                {opt.label}
              </p>
              <p className="text-xs text-gray-500 mt-0.5">{opt.description}</p>
            </button>
          ))}
        </div>

        {error && (
          <p className="mb-3 text-sm text-red-600">{error}</p>
        )}

        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={!hasChanged || isLoading}
            className="flex-1 rounded-lg bg-indigo-600 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 transition disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Saving…" : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
