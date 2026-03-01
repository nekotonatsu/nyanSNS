"use client";

import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { ja } from "date-fns/locale";
import { Heart, MessageCircle, Star } from "lucide-react";
import { apiClient } from "@/lib/api";
import type { Post } from "@/types";
import { cn } from "@/lib/utils";

interface PostCardProps {
  post: Post;
  onUpdate?: (updated: Post) => void;
}

export function PostCard({ post, onUpdate }: PostCardProps) {
  const [liked, setLiked] = useState(post.is_liked);
  const [likesCount, setLikesCount] = useState(post.likes_count);
  const [loading, setLoading] = useState(false);

  const handleLike = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const res = await apiClient.post(`/posts/${post.id}/like`);
      setLiked(res.data.liked);
      setLikesCount((prev) => (res.data.liked ? prev + 1 : prev - 1));
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-lg flex-shrink-0">
          {post.author.display_name[0].toUpperCase()}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 flex-wrap">
            <span className="font-semibold text-gray-900 truncate">{post.author.display_name}</span>
            {post.author.is_priority && (
              <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" title="優先表示ユーザー" />
            )}
            <span className="text-gray-500 text-sm">@{post.author.username}</span>
            <span className="text-gray-400 text-xs ml-auto">
              {formatDistanceToNow(new Date(post.created_at), { addSuffix: true, locale: ja })}
            </span>
          </div>

          <p className="mt-1 text-gray-800 whitespace-pre-wrap break-words">{post.content}</p>

          {post.media_url && (
            <img
              src={post.media_url}
              alt="投稿画像"
              className="mt-2 rounded-lg max-h-80 w-full object-cover"
            />
          )}

          <div className="flex items-center gap-4 mt-3">
            <button
              onClick={handleLike}
              className={cn(
                "flex items-center gap-1 text-sm transition-colors",
                liked ? "text-red-500" : "text-gray-500 hover:text-red-400"
              )}
              disabled={loading}
            >
              <Heart className={cn("w-4 h-4", liked && "fill-current")} />
              <span>{likesCount}</span>
            </button>

            <button className="flex items-center gap-1 text-sm text-gray-500 hover:text-indigo-500 transition-colors">
              <MessageCircle className="w-4 h-4" />
              <span>{post.comments_count}</span>
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
