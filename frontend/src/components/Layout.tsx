import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { organizationsApi } from "../api/client";
import RoleBadge from "./RoleBadge";

interface NavItem {
  label: string;
  to: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", to: "/dashboard" },
];

interface LayoutProps {
  children: React.ReactNode;
}

function formatDate(iso?: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Delete org dialog state
  const [showDeleteOrg, setShowDeleteOrg] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  const handleLogout = async () => {
    setMenuOpen(false);
    await logout();
    navigate("/login", { replace: true });
  };

  const openDeleteOrg = () => {
    setMenuOpen(false);
    setDeleteConfirmText("");
    setDeleteError("");
    setShowDeleteOrg(true);
  };

  const handleDeleteOrg = async () => {
    if (!user?.organization_name) return;
    const expected = `Delete ${user.organization_name}`;
    if (deleteConfirmText !== expected) {
      setDeleteError(`Please type exactly: ${expected}`);
      return;
    }
    setIsDeleting(true);
    setDeleteError("");
    try {
      await organizationsApi.deleteMyOrg(deleteConfirmText);
      await logout();
      navigate("/login", { replace: true });
    } catch {
      setDeleteError("Failed to delete organisation. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white shadow-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          {/* Brand */}
          <div className="flex items-center gap-6">
            <span className="text-xl font-bold tracking-tight text-indigo-600">
              Nexus
            </span>
            {/* Desktop nav */}
            <nav className="hidden gap-5 sm:flex">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`text-sm font-medium transition-colors ${
                    location.pathname === item.to
                      ? "text-indigo-600"
                      : "text-gray-500 hover:text-gray-900"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          {/* User profile button */}
          {user && (
            <div className="relative flex items-center" ref={menuRef}>
              <button
                onClick={() => setMenuOpen((o) => !o)}
                className="flex items-center gap-2 rounded-lg px-2 py-1.5 transition hover:bg-gray-100 active:bg-gray-200"
                aria-label="Open profile menu"
              >
                {user.profile_picture ? (
                  <img
                    src={user.profile_picture}
                    alt={user.name}
                    className="h-8 w-8 shrink-0 rounded-full object-cover ring-2 ring-indigo-100"
                  />
                ) : (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700 ring-2 ring-white">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                )}
                <span className="hidden text-sm font-medium text-gray-700 sm:block">
                  Profile
                </span>
                <svg
                  className="h-4 w-4 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {menuOpen && (
                <div className="absolute right-0 top-full z-20 mt-1.5 w-72 rounded-xl border border-gray-200 bg-white shadow-lg overflow-hidden">
                  {/* Profile header */}
                  <div className="flex items-center gap-3 border-b border-gray-100 bg-gray-50 px-4 py-3">
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
                      <p className="truncate text-sm font-semibold text-gray-900">{user.name}</p>
                      <p className="truncate text-xs text-gray-500">{user.email}</p>
                    </div>
                  </div>

                  {/* Info rows */}
                  <div className="divide-y divide-gray-50 px-4 py-2">
                    <div className="flex items-center justify-between py-2">
                      <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">Organisation</span>
                      <span className="text-sm text-gray-700 font-medium truncate max-w-[140px] text-right">
                        {user.organization_name ?? "—"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between py-2">
                      <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">Date joined</span>
                      <span className="text-sm text-gray-700">{formatDate(user.created_at)}</span>
                    </div>
                    <div className="flex items-center justify-between py-2">
                      <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">Role</span>
                      <RoleBadge role={user.role} />
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="border-t border-gray-100 py-1">
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Sign out
                    </button>

                    {user.role === "admin" && (
                      <button
                        onClick={openDeleteOrg}
                        className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <svg className="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete organisation
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Delete Organisation Dialog */}
      {showDeleteOrg && user && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-100">
                <svg className="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
              </div>
              <div>
                <h2 className="text-base font-semibold text-gray-900">Delete Organisation</h2>
                <p className="text-sm text-gray-500">This action is permanent and cannot be undone.</p>
              </div>
            </div>

            <p className="mb-4 text-sm text-gray-600">
              Deleting <span className="font-semibold text-gray-900">{user.organization_name}</span> will
              permanently remove all members, invitations, and data. To confirm, type:
            </p>
            <p className="mb-3 rounded-lg bg-gray-100 px-3 py-2 font-mono text-sm text-gray-800 select-all">
              Delete {user.organization_name}
            </p>

            <input
              type="text"
              value={deleteConfirmText}
              onChange={(e) => {
                setDeleteConfirmText(e.target.value);
                setDeleteError("");
              }}
              placeholder={`Delete ${user.organization_name}`}
              className="mb-2 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-red-400 focus:outline-none focus:ring-1 focus:ring-red-400"
              autoFocus
            />

            {deleteError && (
              <p className="mb-3 text-xs text-red-600">{deleteError}</p>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowDeleteOrg(false)}
                disabled={isDeleting}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteOrg}
                disabled={isDeleting || deleteConfirmText !== `Delete ${user.organization_name}`}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isDeleting ? "Deleting…" : "Delete organisation"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
