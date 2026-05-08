import { useState } from "react";
import type { ExamplePost } from "@/types";

interface Props {
  examples: ExamplePost[];
  onAnalyze: (input: { url: string; text: string }) => void;
  isAnalyzing: boolean;
}

export function InputBox({ examples, onAnalyze, isAnalyzing }: Props) {
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [showAllExamples, setShowAllExamples] = useState(false);

  const visibleExamples = showAllExamples ? examples : examples.slice(0, 5);

  const handleExampleClick = (ex: ExamplePost) => {
    setUrl(ex.url);
    setText(ex.text);
  };

  const handleAnalyze = () => {
    if (!text.trim()) return;
    onAnalyze({ url: url.trim(), text: text.trim() });
  };

  return (
    <div className="border border-twitter-border bg-white rounded-2xl p-4 mb-3">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-2xl">🔬</span>
        <h2 className="text-lg font-bold text-twitter-text">
          Mode 1 — Test your own content
        </h2>
      </div>
      <p className="text-xs text-twitter-muted mb-3 leading-relaxed">
        Paste any post or article. 6 agents detect manipulation tactics,
        verify claims against authoritative sources, and surface alternative
        perspectives.
      </p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="ตัวอย่าง: โพสต์ขายอาหารเสริมรักษามะเร็ง / โฆษณายาลดน้ำหนัก / บทความ AI-generated สุขภาพ..."
        rows={4}
        className="w-full px-3 py-2 border border-twitter-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-twitter-blue/30 resize-none"
        disabled={isAnalyzing}
      />

      <div className="mt-3">
        <label className="text-xs text-twitter-muted block mb-1">
          🔗 Source URL <span className="text-twitter-muted/70">(optional — adds Provenance Agent credibility check)</span>
        </label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://... (skip if you only have text)"
          className="w-full px-3 py-2 border border-twitter-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-twitter-blue/30"
          disabled={isAnalyzing}
        />
      </div>

      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-md px-2 py-1.5 mt-3">
        💡 Demo MVP optimized for health content. Generic content works but accuracy may vary.
      </p>

      <div className="flex items-center justify-between mt-3">
        <span
          className={`text-xs ${
            text.length > 1000 ? "text-red-600 font-semibold" : "text-twitter-muted"
          }`}
        >
          {text.length}/1000 chars
        </span>
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing || !text.trim()}
          className="bg-twitter-blue hover:bg-twitter-blue/90 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold px-5 py-2 rounded-full text-sm transition-colors"
        >
          {isAnalyzing ? "Analyzing..." : "🔍 Analyze →"}
        </button>
      </div>

      {examples.length > 0 && (
        <div className="mt-4 pt-3 border-t border-twitter-border">
          <p className="text-xs text-twitter-muted mb-2">
            ── OR try an example: ──
          </p>
          <div className="flex flex-wrap gap-2">
            {visibleExamples.map((ex) => (
              <button
                key={ex.id}
                onClick={() => handleExampleClick(ex)}
                disabled={isAnalyzing}
                className="px-3 py-1.5 text-xs rounded-full border border-twitter-border hover:bg-twitter-hover transition-colors disabled:opacity-40"
                title={ex.text.slice(0, 100)}
              >
                {ex.display_emoji} {ex.short_label}
              </button>
            ))}
            {examples.length > 5 && (
              <button
                onClick={() => setShowAllExamples((v) => !v)}
                className="px-3 py-1.5 text-xs text-twitter-blue hover:underline"
              >
                {showAllExamples ? "Show less" : `+ ${examples.length - 5} more`}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
