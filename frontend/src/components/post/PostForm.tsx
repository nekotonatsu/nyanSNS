"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api";
import type { Post } from "@/types";
import { useAuthStore } from "@/store/authStore";

interface PostFormProps {
  onPosted: (post: Post) => void;
}

export function PostForm({ onPosted }: PostFormProps) {
  const { user } = useAuthStore();
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const maxLength = 500;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || loading) return;

    setLoading(true);
    try {
      const res = await apiClient.post<Post>("/posts", { content });
      onPosted(res.data);
      setContent("");
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-xl p-4">
      <div className="flex gap-3">
        <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-lg flex-shrink-0">
          {user.display_name[0].toUpperCase()}
        </div>
        <div className="flex-1">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="いま何を思っていますか？"
            className="w-full resize-none outline-none text-gray-800 placeholder-gray-400 text-sm leading-relaxed min-h-[80px]"
            maxLength={maxLength}
          />
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-100">
            <span className={`text-xs ${content.length > maxLength * 0.9 ? "text-red-400" : "text-gray-400"}`}>
              {content.length} / {maxLength}
            </span>
            <button
              type="submit"
              disabled={!content.trim() || loading}
              className="px-4 py-1.5 bg-indigo-600 text-white text-sm rounded-full font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "投稿中..." : "投稿"}
            </button>
          </div>
        </div>
      </div>
    </form>
  );
}
