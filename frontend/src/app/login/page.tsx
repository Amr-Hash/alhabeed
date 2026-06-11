"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { staffHomePath } from "@/lib/staff";

export default function LoginPage() {
  const { login, user } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) router.replace(staffHomePath(user));
  }, [user, router]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const me = await login(email, password);
      router.push(staffHomePath(me));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  if (user) return null;

  return (
    <div className="mx-auto max-w-md">
      <div className="card">
        <h1 className="mb-6 text-2xl font-bold">Login</h1>
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Password</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          No account?{" "}
          <Link href="/register" className="text-pitch-600 hover:underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
