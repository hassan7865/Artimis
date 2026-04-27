"use client";

import { useEffect, useState } from "react";
import { getConfig, updateKeywords, updateSubreddits, updateAiPrompt } from "@/shared/lib/api";
import { X, Hash, MessageSquare, Save, Plus } from "lucide-react";

export default function SettingsPage() {
  const [keywords, setKeywords] = useState<string[]>([]);
  const [subreddits, setSubreddits] = useState<string[]>([]);
  const [aiPrompt, setAiPrompt] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const [newKeyword, setNewKeyword] = useState("");
  const [newSubreddit, setNewSubreddit] = useState("");

  useEffect(() => {
    getConfig().then((cfg) => {
      setKeywords(cfg.keywords);
      setSubreddits(cfg.subreddits);
      setAiPrompt(cfg.ai_prompt || "");
      setLoading(false);
    });
  }, []);

  const handleAddKeyword = () => {
    if (!newKeyword.trim()) return;
    setKeywords([...keywords, newKeyword.trim()]);
    setNewKeyword("");
  };

  const handleRemoveKeyword = (index: number) => {
    setKeywords(keywords.filter((_, i) => i !== index));
  };

  const handleAddSubreddit = () => {
    if (!newSubreddit.trim()) return;
    setSubreddits([...subreddits, newSubreddit.trim().replace(/^r\//, "")]);
    setNewSubreddit("");
  };

  const handleRemoveSubreddit = (index: number) => {
    setSubreddits(subreddits.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateKeywords(keywords);
      await updateSubreddits(subreddits);
      await updateAiPrompt(aiPrompt);
      alert("Settings saved successfully!");
    } catch (error) {
      alert("Failed to save settings.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="py-20 text-center text-slate-500">Loading configuration...</div>;

  return (
    <div className="flex flex-col gap-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">System Settings</h1>
          <p className="text-slate-500">Configure your target keywords and subreddits for monitoring.</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="rounded-xl bg-slate-900 px-8 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:bg-slate-400 flex items-center gap-2"
        >
          <Save size={16} />
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </header>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Keywords Section */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Hash className="text-blue-500" size={20} />
            <h2 className="text-xl font-bold text-slate-900">Keywords</h2>
          </div>
          <div className="mb-6 flex gap-2">
            <input
              type="text"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              placeholder="Add keyword (e.g. need a developer)"
              className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none"
              onKeyPress={(e) => e.key === "Enter" && handleAddKeyword()}
            />
            <button
              onClick={handleAddKeyword}
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-bold text-white hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus size={16} /> Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700">
                {kw}
                <button onClick={() => handleRemoveKeyword(i)} className="text-slate-400 hover:text-red-500 transition-colors">
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Subreddits Section */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <MessageSquare className="text-orange-500" size={20} />
            <h2 className="text-xl font-bold text-slate-900">Subreddits</h2>
          </div>
          <div className="mb-6 flex gap-2">
            <input
              type="text"
              value={newSubreddit}
              onChange={(e) => setNewSubreddit(e.target.value)}
              placeholder="Add subreddit (e.g. forhire)"
              className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none"
              onKeyPress={(e) => e.key === "Enter" && handleAddSubreddit()}
            />
            <button
              onClick={handleAddSubreddit}
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-bold text-white hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus size={16} /> Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {subreddits.map((sub, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg bg-orange-50 px-3 py-1.5 text-sm font-bold text-orange-700">
                r/{sub}
                <button onClick={() => handleRemoveSubreddit(i)} className="text-orange-300 hover:text-red-500 transition-colors">
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* AI Prompt Section */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare className="text-indigo-500" size={20} />
          <h2 className="text-xl font-bold text-slate-900">AI Analysis Prompt</h2>
        </div>
        <p className="text-sm text-slate-500 mb-4">
          Customize how the AI evaluates posts. Define what counts as a "technical lead" and set your own disqualification criteria.
        </p>
        <textarea
          value={aiPrompt}
          onChange={(e) => setAiPrompt(e.target.value)}
          rows={12}
          className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm font-mono focus:border-indigo-500 focus:outline-none"
          placeholder="Enter the AI system prompt here..."
        />
      </section>
    </div>
  );
}
