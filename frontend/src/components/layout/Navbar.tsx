"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Home, MessageCircle, User, LogOut } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { clearAuthCookies } from "@/lib/api";

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    clearAuthCookies();
    logout();
    router.push("/login");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/feed" className="text-xl font-bold text-indigo-600">
          nyanSNS
        </Link>

        {isAuthenticated && user ? (
          <div className="flex items-center gap-4">
            <Link href="/feed" className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <Home className="w-5 h-5 text-gray-700" />
            </Link>
            <Link href="/messages" className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <MessageCircle className="w-5 h-5 text-gray-700" />
            </Link>
            <Link href={`/profile/${user.username}`} className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <User className="w-5 h-5 text-gray-700" />
            </Link>
            <button
              onClick={handleLogout}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            >
              <LogOut className="w-5 h-5 text-gray-700" />
            </button>
          </div>
        ) : (
          <div className="flex gap-2">
            <Link
              href="/login"
              className="px-4 py-2 text-sm text-indigo-600 border border-indigo-600 rounded-full hover:bg-indigo-50 transition-colors"
            >
              ログイン
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 text-sm text-white bg-indigo-600 rounded-full hover:bg-indigo-700 transition-colors"
            >
              登録
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
