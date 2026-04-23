"use client";

import { useState, useEffect } from "react";
import {
  Phone, Settings, Play, RefreshCw, Mic, Volume2, FileText,
  Wrench, Save, Loader2, CheckCircle, XCircle
} from "lucide-react";
import { vapiApi, assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

export default function VoiceAgentControlCenter() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("overview");
  const [assistant, setAssistant] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [firstMessage, setFirstMessage] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await vapiApi.getMyAssistant();
      setAssistant(data);
      if (data.configured) {
        try {
          const personality = await assistantApi.getPersonality();
          setFirstMessage(personality.first_message || "");
          setSystemPrompt(personality.system_prompt || "");
        } catch { }
      }
    } catch (error) {
      console.error("Failed to load assistant:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const savePersonality = async () => {
    try {
      setSaving(true);
      await assistantApi.updatePersonality({
        first_message: firstMessage,
        system_prompt: systemPrompt,
        temperature: 0.7
      });
      toast({ title: "Saved", description: "Personality updated successfully" });
    } catch (error) {
      console.error("Save failed:", error);
      toast({ title: "Error", description: "Failed to save changes", variant: "destructive" });
    } finally {
      setSaving(false);
    }
  };

  const navCards = [
    { href: "/dashboard/voice-agent/voice", icon: Volume2, label: "Voice", desc: "Configure voice", color: "from-blue-500 to-blue-600" },
    { href: "/dashboard/voice-agent/knowledge-base", icon: FileText, label: "Knowledge Base", desc: "Upload docs", color: "from-[#187848] to-[#0a4c2f]" },
    { href: "/dashboard/voice-agent/tools", icon: Wrench, label: "Tools", desc: "Enable features", color: "from-purple-500 to-purple-600" },
  ];

  const tabs = [
    { id: "overview", label: "Overview", icon: Mic },
    { id: "personality", label: "Quick Edit", icon: Settings },
  ];

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">AI Receptionist</h1>
          <p className="text-[14px] text-gray-500 font-medium">Configure and manage your voice AI assistant.</p>
        </div>
        <div className="flex gap-2">
          <Link href="/dashboard/voice-agent/test" className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-[20px] font-semibold hover:bg-gray-50 transition-colors flex items-center gap-2 text-sm shadow-sm">
            <Play className="w-4 h-4" />
            Test Call
          </Link>
          <button onClick={loadData} disabled={loading} className="p-2.5 bg-white border border-gray-200 text-gray-700 rounded-full hover:bg-gray-50 transition-colors shadow-sm">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Quick Nav Cards */}
      <div className="grid gap-4 md:grid-cols-3 mb-8">
        {navCards.map((card) => (
          <Link key={card.href} href={card.href} className="bg-white rounded-[20px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-5 hover:shadow-md transition-shadow group">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl bg-gradient-to-br ${card.color} text-white`}>
                <card.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="font-bold text-gray-900">{card.label}</p>
                <p className="text-sm text-gray-500">{card.desc}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-white rounded-full p-1 border border-gray-100 w-fit shadow-sm">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-full font-semibold text-sm transition-colors flex items-center gap-2 ${activeTab === tab.id ? 'bg-[#0a4c2f] text-white' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
              }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
          <h3 className="font-bold text-lg text-gray-900 mb-4">Assistant Status</h3>
          <p className="text-sm text-gray-500 mb-6">Current configuration</p>
          {loading ? (
            <div className="flex justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin text-[#0a4c2f]" />
            </div>
          ) : (
            <div className="space-y-3">
              {[
                {
                  label: "Status", value: assistant?.configured ? (
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700 flex items-center gap-1"><CheckCircle className="w-3 h-3" />Active</span>
                  ) : (
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 flex items-center gap-1"><XCircle className="w-3 h-3" />Not Configured</span>
                  )
                },
                { label: "Assistant ID", value: <code className="text-xs bg-gray-100 px-2 py-1 rounded-lg text-gray-700">{assistant?.assistant_id?.slice(0, 12) || 'N/A'}...</code> },
                { label: "Voice", value: <span className="text-sm text-gray-900 font-medium">{assistant?.voice?.voiceId?.slice(0, 10) || 'Default'}...</span> },
                { label: "Model", value: <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-700">{assistant?.model?.model || 'gpt-4o-mini'}</span> },
              ].map((row, i) => (
                <div key={i} className="flex justify-between items-center p-3.5 bg-gray-50 rounded-xl">
                  <span className="font-medium text-gray-700">{row.label}</span>
                  {row.value}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "personality" && (
        <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-lg text-gray-900">Personality & Prompt</h3>
              <p className="text-sm text-gray-500">Customize how your AI responds</p>
            </div>
            <button onClick={savePersonality} disabled={saving} className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
              {saving ? <Loader2 className="w-4 h-4 mr-1 animate-spin relative z-10" /> : <Save className="w-4 h-4 mr-1 relative z-10" />}
              <span className="relative z-10">Save Changes</span>
            </button>
          </div>

          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">First Message (Greeting)</label>
              <input
                value={firstMessage}
                onChange={(e) => setFirstMessage(e.target.value)}
                placeholder="Hello! Thank you for calling..."
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all"
              />
              <p className="text-xs text-gray-400">What the AI says when answering a call</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-gray-700">System Prompt (Instructions)</label>
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder="You are a helpful AI receptionist..."
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 transition-all min-h-[200px] font-mono resize-none"
              />
              <p className="text-xs text-gray-400">Detailed instructions for how the AI should behave</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
