import { useState } from "react";
import { usersApi } from "../api/client";
import type { User } from "../types";

interface DeleteUserDialogProps {
  user: User;
  onClose: () => void;
  onSuccess: (userId: string) => void;
}

export default function DeleteUserDialog({ user, onClose, onSuccess }: DeleteUserDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleDelete = async () => {
    setIsLoading(true);
    setError("");
    try {
      await usersApi.deleteUser(user.id);
      onSuccess(user.id);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? "Failed to remove member. Please try again.");
      setIsLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
          <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        </div>

        <h2 className="text-lg font-semibold text-gray-900">Remove member</h2>
        <p className="mt-2 text-sm text-gray-500">
          Are you sure you want to remove{" "}
          <span className="font-medium text-gray-800">{user.name}</span> from the
          organization? This action cannot be undone.
        </p>

        {error && (
          <p className="mt-3 text-sm text-red-600">{error}</p>
        )}

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleDelete}
            disabled={isLoading}
            className="flex-1 rounded-lg bg-red-600 py-2.5 text-sm font-medium text-white hover:bg-red-700 transition disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Removing…" : "Remove"}
          </button>
        </div>
      </div>
    </div>
  );
}
