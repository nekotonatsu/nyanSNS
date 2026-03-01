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

const registerSchema = z.object({
  username: z.string().min(3, "3文字以上").max(50).regex(/^[a-zA-Z0-9_]+$/, "英数字とアンダースコアのみ"),
  email: z.string().email("有効なメールアドレスを入力してください"),
  display_name: z.string().min(1, "表示名を入力してください").max(100),
  password: z.string().min(8, "8文字以上のパスワードを入力してください"),
});

const otpSchema = z.object({
  otp_code: z.string().length(6, "6桁のコードを入力してください"),
});

type RegisterForm = z.infer<typeof registerSchema>;
type OTPForm = z.infer<typeof otpSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { setUser } = useAuthStore();
  const [step, setStep] = useState<"register" | "otp">("register");
  const [tempToken, setTempToken] = useState("");
  const [error, setError] = useState("");

  const registerForm = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });
  const otpForm = useForm<OTPForm>({ resolver: zodResolver(otpSchema) });

  const onRegister = async (data: RegisterForm) => {
    setError("");
    try {
      const res = await apiClient.post<TempTokenResponse>("/auth/register", data);
      setTempToken(res.data.temp_token);
      setStep("otp");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || "登録に失敗しました");
      }
    }
  };

  const onOTP = async (data: OTPForm) => {
    setError("");
    try {
      const res = await apiClient.post<TokenResponse>("/auth/register/verify-otp", {
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

        {step === "register" ? (
          <>
            <h2 className="text-lg font-semibold mb-4 text-gray-800">アカウント登録</h2>
            <form onSubmit={registerForm.handleSubmit(onRegister)} className="space-y-4">
              {(["username", "email", "display_name", "password"] as const).map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {{ username: "ユーザー名", email: "メールアドレス", display_name: "表示名", password: "パスワード" }[field]}
                  </label>
                  <input
                    {...registerForm.register(field)}
                    type={field === "password" ? "password" : field === "email" ? "email" : "text"}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  />
                  {registerForm.formState.errors[field] && (
                    <p className="text-red-500 text-xs mt-1">{registerForm.formState.errors[field]?.message}</p>
                  )}
                </div>
              ))}

              {error && <p className="text-red-500 text-sm">{error}</p>}

              <button
                type="submit"
                disabled={registerForm.formState.isSubmitting}
                className="w-full bg-indigo-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {registerForm.formState.isSubmitting ? "登録中..." : "登録"}
              </button>
            </form>

            <p className="text-sm text-center text-gray-500 mt-4">
              すでにアカウントをお持ちの方は{" "}
              <Link href="/login" className="text-indigo-600 hover:underline">ログイン</Link>
            </p>
          </>
        ) : (
          <>
            <h2 className="text-lg font-semibold mb-2 text-gray-800">OTP設定</h2>
            <p className="text-sm text-gray-500 mb-4">
              認証アプリ（Google Authenticator等）で <code className="bg-gray-100 px-1 rounded">/auth/otp/setup</code> のQRコードをスキャンするか、
              メールで届いたコードを入力してください
            </p>

            <form onSubmit={otpForm.handleSubmit(onOTP)} className="space-y-4">
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

              {error && <p className="text-red-500 text-sm">{error}</p>}

              <button
                type="submit"
                disabled={otpForm.formState.isSubmitting}
                className="w-full bg-indigo-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {otpForm.formState.isSubmitting ? "確認中..." : "確認して完了"}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
