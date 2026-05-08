import type { AnalysisResult, MockPost } from "@/types";
import type { Strictness } from "@/lib/preferences";
import { PostCard } from "./PostCard";

interface Props {
  posts: MockPost[];
  onAnalyzePost: (post: MockPost) => void;
  postResults: Record<string, AnalysisResult>;
  postAnalyzing: Record<string, boolean>;
  focusedPostId: string | null;
  onFocusPost: (postId: string, agentId?: string) => void;
  onLinkClick?: (post: MockPost, url: string) => void;
  strictness: Strictness;
  overriddenPostIds: string[];
}

export function Feed({
  posts,
  onAnalyzePost,
  postResults,
  postAnalyzing,
  focusedPostId,
  onFocusPost,
  onLinkClick,
  strictness,
  overriddenPostIds,
}: Props) {
  return (
    <div className="border border-twitter-border bg-white rounded-2xl overflow-hidden">
      <div className="px-4 py-3 border-b border-twitter-border">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xl">📰</span>
          <h2 className="font-bold text-lg text-twitter-text">
            Mode 2 — Watch agents protect you in social media
          </h2>
        </div>
        <p className="text-xs text-twitter-muted leading-relaxed">
          Scroll the curated feed below. As each post enters view, all 6 agents
          analyze it automatically. Click <span className="font-semibold">[📊 See full →]</span> for deeper detail.
        </p>
        <p className="text-[10px] text-amber-700 mt-1.5 italic leading-relaxed">
          💡 ML pre-computed for demo · text: Hello-SimpleAI · image: prithivMLmods/deepfake-detector-v1 · video: eftt/VideoMae-ffc23 · transcript: STT (offline)
        </p>
      </div>

      {posts.length === 0 ? (
        <div className="px-4 py-8 text-center text-twitter-muted text-sm">
          No posts yet — Suim populates the feed during Step 6B.
        </div>
      ) : (
        <div>
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onAnalyze={onAnalyzePost}
              analysis={postResults[post.id]}
              isAnalyzing={Boolean(postAnalyzing[post.id])}
              isFocused={focusedPostId === post.id}
              onFocus={onFocusPost}
              onLinkClick={onLinkClick}
              strictness={strictness}
              isOverridden={overriddenPostIds.includes(post.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
