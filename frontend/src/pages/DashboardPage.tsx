import { useEffect, useMemo, useState } from "react";
import { usersApi, invitationsApi } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Invitation, User, UserRole, UserStatus } from "../types";
import UserCard from "../components/UserCard";
import InviteUserModal from "../components/InviteUserModal";
import EditRoleModal from "../components/EditRoleModal";
import DeleteUserDialog from "../components/DeleteUserDialog";
import { ToastContainer } from "../components/Toast";
import { useToast } from "../hooks/useToast";

const ROLE_FILTERS: { value: UserRole | "all"; label: string }[] = [
  { value: "all", label: "All roles" },
  { value: "admin", label: "Admin" },
  { value: "manager", label: "Manager" },
  { value: "viewer", label: "Viewer" },
];

const STATUS_FILTERS: { value: UserStatus | "all"; label: string }[] = [
  { value: "all", label: "All statuses" },
  { value: "active", label: "Active" },
  { value: "pending", label: "Pending" },
];

export default function DashboardPage() {
  const { user: currentUser } = useAuth();
  const { toasts, addToast, dismissToast } = useToast();

  const [users, setUsers] = useState<User[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<UserRole | "all">("all");
  const [statusFilter, setStatusFilter] = useState<UserStatus | "all">("all");

  const [showInviteModal, setShowInviteModal] = useState(false);
  const [editRoleTarget, setEditRoleTarget] = useState<User | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);

  const canManage =
    currentUser?.role === "admin" || currentUser?.role === "manager";

  const fetchData = async () => {
    setIsLoading(true);
    setError("");
    try {
      const [usersRes, invitesRes] = await Promise.all([
        usersApi.list(),
        canManage ? invitationsApi.list() : Promise.resolve({ data: [] }),
      ]);
      setUsers(usersRes.data);
      setInvitations(invitesRes.data);
    } catch {
      setError("Failed to load team data. Please refresh.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filteredUsers = useMemo(() => {
    const q = search.toLowerCase().trim();
    return users.filter((u) => {
      const matchesSearch =
        !q || u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q);
      const matchesRole = roleFilter === "all" || u.role === roleFilter;
      const matchesStatus = statusFilter === "all" || u.status === statusFilter;
      return matchesSearch && matchesRole && matchesStatus;
    });
  }, [users, search, roleFilter, statusFilter]);

  const hasActiveFilters =
    search !== "" || roleFilter !== "all" || statusFilter !== "all";

  if (!currentUser) return null;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Team</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your organization's members and roles.
          </p>
        </div>
        {canManage && (
          <button
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 transition"
            onClick={() => setShowInviteModal(true)}
          >
            + Invite member
          </button>
        )}
      </div>

      {/* Error state */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Search + filters */}
      {!isLoading && (
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <svg
              className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
            </svg>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name or email…"
              className="w-full rounded-lg border border-gray-300 py-2 pl-9 pr-3 text-sm shadow-sm placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value as UserRole | "all")}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {ROLE_FILTERS.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as UserStatus | "all")}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {STATUS_FILTERS.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>

          {hasActiveFilters && (
            <button
              onClick={() => { setSearch(""); setRoleFilter("all"); setStatusFilter("all"); }}
              className="text-sm text-indigo-600 hover:underline"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Loading skeleton */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-16 animate-pulse rounded-xl bg-gray-100" />
          ))}
        </div>
      ) : (
        <>
          {/* Members list */}
          <section>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
              Members ({filteredUsers.length}
              {hasActiveFilters && users.length !== filteredUsers.length
                ? ` of ${users.length}`
                : ""})
            </h2>
            {filteredUsers.length === 0 ? (
              <div className="rounded-xl border border-dashed border-gray-300 py-10 text-center">
                <p className="text-sm text-gray-500">
                  {hasActiveFilters ? "No members match your filters." : "No members yet."}
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredUsers.map((u) => (
                  <UserCard
                    key={u.id}
                    user={u}
                    currentUserRole={currentUser.role}
                    onChangeRole={setEditRoleTarget}
                    onDelete={setDeleteTarget}
                  />
                ))}
              </div>
            )}
          </section>

          {/* Pending invitations */}
          {canManage && invitations.length > 0 && (statusFilter === "all" || statusFilter === "pending") && (
            <section>
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
                Pending Invitations ({invitations.length})
              </h2>
              <div className="space-y-2">
                {invitations.map((inv) => (
                  <div
                    key={inv.id}
                    className="flex items-center justify-between rounded-xl border border-dashed border-gray-300 bg-white px-5 py-3"
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-800">{inv.name}</p>
                      <p className="text-xs text-gray-500">{inv.email}</p>
                    </div>
                    <span className="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-700">
                      Invited · {inv.role}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}

      {/* Modals */}
      {showInviteModal && (
        <InviteUserModal
          currentUserRole={currentUser.role}
          onClose={() => setShowInviteModal(false)}
          onSuccess={(inv) => {
            setInvitations((prev) => [inv, ...prev]);
            setShowInviteModal(false);
            addToast(`Invitation sent to ${inv.email}`, "success");
          }}
        />
      )}

      {editRoleTarget && (
        <EditRoleModal
          user={editRoleTarget}
          currentUserRole={currentUser.role}
          onClose={() => setEditRoleTarget(null)}
          onSuccess={(updated) => {
            setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
            setEditRoleTarget(null);
            addToast(`${updated.name}'s role updated to ${updated.role}`, "success");
          }}
        />
      )}

      {deleteTarget && (
        <DeleteUserDialog
          user={deleteTarget}
          onClose={() => setDeleteTarget(null)}
          onSuccess={(deletedId) => {
            const removed = users.find((u) => u.id === deletedId);
            setUsers((prev) => prev.filter((u) => u.id !== deletedId));
            setDeleteTarget(null);
            if (removed) addToast(`${removed.name} has been removed`, "info");
          }}
        />
      )}

      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
