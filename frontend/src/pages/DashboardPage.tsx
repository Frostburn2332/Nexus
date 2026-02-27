import { useEffect, useState } from "react";
import { usersApi, invitationsApi } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Invitation, User } from "../types";
import UserCard from "../components/UserCard";
import InviteUserModal from "../components/InviteUserModal";
import EditRoleModal from "../components/EditRoleModal";
import DeleteUserDialog from "../components/DeleteUserDialog";

export default function DashboardPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
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

  if (!currentUser) return null;

  return (
    <div className="space-y-8">
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

      {/* Loading skeleton */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-16 animate-pulse rounded-xl bg-gray-100"
            />
          ))}
        </div>
      ) : (
        <>
          {/* Active members */}
          <section>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-400">
              Members ({users.length})
            </h2>
            {users.length === 0 ? (
              <p className="text-sm text-gray-500">No members yet.</p>
            ) : (
              <div className="space-y-3">
                {users.map((u) => (
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
          {canManage && invitations.length > 0 && (
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
                      <p className="text-sm font-medium text-gray-800">
                        {inv.name}
                      </p>
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

      {showInviteModal && (
        <InviteUserModal
          onClose={() => setShowInviteModal(false)}
          onSuccess={(inv) => {
            setInvitations((prev) => [inv, ...prev]);
            setShowInviteModal(false);
          }}
        />
      )}

      {editRoleTarget && (
        <EditRoleModal
          user={editRoleTarget}
          onClose={() => setEditRoleTarget(null)}
          onSuccess={(updated) => {
            setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
            setEditRoleTarget(null);
          }}
        />
      )}

      {deleteTarget && (
        <DeleteUserDialog
          user={deleteTarget}
          onClose={() => setDeleteTarget(null)}
          onSuccess={(deletedId) => {
            setUsers((prev) => prev.filter((u) => u.id !== deletedId));
            setDeleteTarget(null);
          }}
        />
      )}
    </div>
  );
}
