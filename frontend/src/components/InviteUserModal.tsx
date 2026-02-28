import { type FormEvent, useState } from "react";
import { invitationsApi } from "../api/client";
import type { Invitation, UserRole } from "../types";

interface InviteUserModalProps {
  currentUserRole: UserRole;
  onClose: () => void;
  onSuccess: (invitation: Invitation) => void;
}

const ALL_ROLE_OPTIONS: { value: UserRole; label: string }[] = [
  { value: "viewer", label: "Viewer" },
  { value: "manager", label: "Manager" },
  { value: "admin", label: "Admin" },
];

export default function InviteUserModal({
  currentUserRole,
  onClose,
  onSuccess,
}: InviteUserModalProps) {
  const ROLE_OPTIONS = currentUserRole === "admin"
    ? ALL_ROLE_OPTIONS
    : ALL_ROLE_OPTIONS.filter((o) => o.value !== "admin");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<UserRole>("viewer");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [createdInvitation, setCreatedInvitation] = useState<Invitation | null>(null);

  const inviteLink = createdInvitation
    ? `${window.location.origin}/invite/accept?token=${createdInvitation.token}`
    : null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !name.trim()) {
      setError("Email and name are required.");
      return;
    }
    setError("");
    setIsLoading(true);
    try {
      const { data } = await invitationsApi.create({ email: email.trim(), name: name.trim(), role });
      setCreatedInvitation(data);
      onSuccess(data);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? "Failed to send invitation. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyLink = () => {
    if (inviteLink) navigator.clipboard.writeText(inviteLink);
  };

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Invite member</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition"
          >
            ✕
          </button>
        </div>

        {/* Success state — show invite link */}
        {createdInvitation ? (
          <div className="space-y-4">
            <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
              Invitation created for <strong>{createdInvitation.email}</strong>.
            </div>
            <div>
              <p className="mb-1.5 text-xs font-medium text-gray-500 uppercase tracking-wide">
                Invitation link
              </p>
              <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
                <span className="flex-1 truncate text-xs text-gray-700 font-mono">
                  {inviteLink}
                </span>
                <button
                  onClick={handleCopyLink}
                  className="shrink-0 rounded-md px-2.5 py-1 text-xs font-medium text-indigo-600 border border-indigo-200 hover:bg-indigo-50 transition"
                >
                  Copy
                </button>
              </div>
              <p className="mt-1.5 text-xs text-gray-400">
                Share this link with the invitee. It expires in 7 days.
              </p>
            </div>
            <button
              onClick={onClose}
              className="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 transition"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Full name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Smith"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane@company.com"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {ROLE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}

            <div className="flex gap-3 pt-1">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 rounded-lg bg-indigo-600 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 transition disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? "Sending…" : "Send invitation"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
