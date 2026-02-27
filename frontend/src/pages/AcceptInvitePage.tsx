import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

type PageState = "idle" | "loading" | "error_no_token" | "error_mismatch" | "error_generic";

export default function AcceptInvitePage() {
  const { loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const token = searchParams.get("token");
  const [pageState, setPageState] = useState<PageState>("idle");

  // Surface errors forwarded by the backend via redirect query params
  useEffect(() => {
    if (!token) {
      setPageState("error_no_token");
      return;
    }

    const errorParam = searchParams.get("error");
    if (errorParam === "email_mismatch") {
      setPageState("error_mismatch");
    }
  }, [token, searchParams]);

  const handleAccept = async () => {
    if (!token) return;
    setPageState("loading");
    try {
      await loginWithGoogle("invite", { invitation_token: token });
    } catch {
      setPageState("error_generic");
    }
  };

  if (pageState === "error_no_token") {
    return <ErrorCard title="Invalid invitation link" message="This invitation link is missing a token. Please ask your admin to resend the invitation." />;
  }

  if (pageState === "error_mismatch") {
    return (
      <ErrorCard
        title="Wrong Google account"
        message="The Google account you signed in with doesn't match the email address this invitation was sent to. Please sign in with the correct account."
        action={
          <button
            onClick={handleAccept}
            className="mt-4 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 transition"
          >
            Try again
          </button>
        }
      />
    );
  }

  if (pageState === "error_generic") {
    return (
      <ErrorCard
        title="Something went wrong"
        message="We couldn't process your invitation. The link may have expired or already been used."
        action={
          <button
            onClick={() => navigate("/login")}
            className="mt-4 rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
          >
            Go to login
          </button>
        }
      />
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm text-center">
          <span className="text-3xl font-bold tracking-tight text-indigo-600">
            Nexus
          </span>
          <h1 className="mt-3 text-xl font-semibold text-gray-900">
            You've been invited
          </h1>
          <p className="mt-2 text-sm text-gray-500">
            Accept this invitation to join your team's workspace. You'll be asked
            to sign in with Google to verify your identity.
          </p>

          <button
            onClick={handleAccept}
            disabled={pageState === "loading"}
            className="mt-6 flex w-full items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>
            {pageState === "loading" ? "Redirecting to Google…" : "Accept with Google"}
          </button>

          <p className="mt-4 text-xs text-gray-400">
            Your Google account email must match the address this invitation was sent to.
          </p>
        </div>
      </div>
    </div>
  );
}

interface ErrorCardProps {
  title: string;
  message: string;
  action?: React.ReactNode;
}

function ErrorCard({ title, message, action }: ErrorCardProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-sm text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
          <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        </div>
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        <p className="mt-2 text-sm text-gray-500">{message}</p>
        {action}
      </div>
    </div>
  );
}
