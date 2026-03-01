"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import axios from "axios";
import { apiClient, setAuthCookies } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import type { TokenResponse, TempTokenResponse, UserRead } from "@/types";

const loginSchema = z.object({
  email: z.string().email("有効なメールアドレスを入力してください"),
  password: z.string().min(1, "パスワードを入力してください"),
});

const otpSchema = z.object({
  otp_code: z.string().length(6, "6桁のコードを入力してください"),
});

type LoginForm = z.infer<typeof loginSchema>;
type OTPForm = z.infer<typeof otpSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { setUser } = useAuthStore();
  const [step, setStep] = useState<"login" | "otp">("login");
  const [tempToken, setTempToken] = useState("");
  const [error, setError] = useState("");

  const loginForm = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });
  const otpForm = useForm<OTPForm>({ resolver: zodResolver(otpSchema) });

  const onLogin = async (data: LoginForm) => {
    setError("");
    try {
      const res = await apiClient.post<TokenResponse | TempTokenResponse>("/auth/login", data);
      if ("requires_otp" in res.data && res.data.requires_otp) {
        setTempToken(res.data.temp_token);
        setStep("otp");
      } else {
        const tokens = res.data as TokenResponse;
        setAuthCookies(tokens.access_token, tokens.refresh_token);
        const me = await apiClient.get<UserRead>("/users/me");
        setUser(me.data);
        router.push("/feed");
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || "ログインに失敗しました");
      }
    }
  };

  const onOTP = async (data: OTPForm) => {
    setError("");
    try {
      const res = await apiClient.post<TokenResponse>("/auth/login/verify-otp", {
        temp_token: tempToken,
        otp_code: data.otp_code,
      });
      setAuthCookies(res.data.access_token, res.data.refresh_token);
      const me = await apiClient.get<UserRead>("/users/me");
      setUser(me.data);
      router.push("/feed");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || "OTP検証に失敗しました");
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-center text-indigo-600 mb-6">nyanSNS</h1>

        {step === "login" ? (
          <>
            <h2 className="text-lg font-semibold mb-4 text-gray-800">ログイン</h2>
            <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">メールアドレス</label>
                <input
                  {...loginForm.register("email")}
                  type="email"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                {loginForm.formState.errors.email && (
                  <p className="text-red-500 text-xs mt-1">{loginForm.formState.errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">パスワード</label>
                <input
                  {...loginForm.register("password")}
                  type="password"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>

              {error && <p className="text-red-500 text-sm">{error}</p>}

              <button
                type="submit"
                disabled={loginForm.formState.isSubmitting}
                className="w-full bg-indigo-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {loginForm.formState.isSubmitting ? "ログイン中..." : "ログイン"}
              </button>
            </form>

            <p className="text-sm text-center text-gray-500 mt-4">
              アカウントをお持ちでない方は{" "}
              <Link href="/register" className="text-indigo-600 hover:underline">登録</Link>
            </p>
          </>
        ) : (
          <>
            <h2 className="text-lg font-semibold mb-2 text-gray-800">OTP確認</h2>
            <p className="text-sm text-gray-500 mb-4">認証アプリに表示された6桁のコードを入力してください</p>

            <form onSubmit={otpForm.handleSubmit(onOTP)} className="space-y-4">
              <div>
                <input
                  {...otpForm.register("otp_code")}
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  placeholder="000000"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-center text-2xl tracking-widest focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
                {otpForm.formState.errors.otp_code && (
                  <p className="text-red-500 text-xs mt-1">{otpForm.formState.errors.otp_code.message}</p>
                )}
              </div>

              {error && <p className="text-red-500 text-sm">{error}</p>}

              <button
                type="submit"
                disabled={otpForm.formState.isSubmitting}
                className="w-full bg-indigo-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {otpForm.formState.isSubmitting ? "確認中..." : "確認"}
              </button>

              <button
                type="button"
                onClick={() => setStep("login")}
                className="w-full text-sm text-gray-500 hover:text-gray-700"
              >
                戻る
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
