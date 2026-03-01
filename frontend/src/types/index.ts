export interface UserPublic {
  id: number;
  username: string;
  display_name: string;
  bio: string | null;
  avatar_url: string | null;
  is_priority: boolean;
  created_at: string;
}

export interface UserRead extends UserPublic {
  email: string;
  score: number;
  otp_enabled: boolean;
  is_active: boolean;
}

export interface Post {
  id: number;
  author_id: number;
  author: UserPublic;
  content: string;
  media_url: string | null;
  media_type: string | null;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  post_id: number;
  author: UserPublic;
  content: string;
  parent_id: number | null;
  replies: Comment[];
  created_at: string;
}

export interface Message {
  id: number;
  sender_id: number;
  receiver_id: number;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TempTokenResponse {
  temp_token: string;
  requires_otp: boolean;
}
