"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { Navbar } from "@/components/layout/Navbar";
import { PostCard } from "@/components/post/PostCard";
import { PostForm } from "@/components/post/PostForm";
import type { Post } from "@/types";

export default function FeedPage() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    fetchPosts();
  }, [isAuthenticated]);

  const fetchPosts = async () => {
    try {
      const res = await apiClient.get<Post[]>("/posts");
      setPosts(res.data);
    } finally {
      setLoading(false);
    }
  };

  const handlePosted = (post: Post) => {
    setPosts((prev) => [post, ...prev]);
  };

  return (
    <>
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 pt-20 pb-10">
        <div className="space-y-4">
          <PostForm onPosted={handlePosted} />

          {loading ? (
            <div className="text-center py-8 text-gray-400">読み込み中...</div>
          ) : posts.length === 0 ? (
            <div className="text-center py-8 text-gray-400">投稿がありません</div>
          ) : (
            posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))
          )}
        </div>
      </main>
    </>
  );
}
