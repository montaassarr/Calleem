"use client";

import { useState, useEffect, useCallback } from "react";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Loader2, Volume2, Play, Save, Check } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

// `provider` is set on voices of the "Tunisian voices" group, which mixes providers.
interface Voice { id: string; name: string; gender: string; accent: string; provider?: string; }
interface VoiceProvider { id: string; name: string; description: string; voices: Voice[]; }
interface LanguageOption { id: string; label: string; native_label: string; }

const PREVIEW_TEXT: Record<string, string> = {
    en: "Hello! Thank you for calling. How can I help you today?",
    "ar-TN": "عسلامة، مرحبا بيك! كيفاش نجّم نعاونك؟",
};

export default function VoiceConfigPage() {
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [providers, setProviders] = useState<VoiceProvider[]>([]);
    const [currentVoice, setCurrentVoice] = useState<any>(null);
    const [selectedProvider, setSelectedProvider] = useState("11labs");
    const [selectedVoice, setSelectedVoice] = useState("");
    const [voiceSpeed, setVoiceSpeed] = useState([1.0]);
    const [previewText, setPreviewText] = useState(PREVIEW_TEXT.en);
    const [language, setLanguage] = useState("en");
    const [languages, setLanguages] = useState<LanguageOption[]>([]);
    const [switchingTo, setSwitchingTo] = useState<string | null>(null);

    const loadData = useCallback(async () => {
        try {
            setLoading(true);
            const [providersData, voiceData, languageData] = await Promise.all([assistantApi.getVoiceProviders(), assistantApi.getVoice(), assistantApi.getLanguage()]);
            const groups: VoiceProvider[] = providersData.providers || [];
            setProviders(groups); setCurrentVoice(voiceData.voice || {});
            setLanguage(languageData.language || "en"); setLanguages(languageData.options || []);
            setPreviewText(PREVIEW_TEXT[languageData.language] || PREVIEW_TEXT.en);
            if (voiceData.voice) {
                const voiceId = voiceData.voice.voiceId || "";
                const tunisianGroup = groups.find(g => g.id === "tunisian" && g.voices.some(v => v.id === voiceId));
                setSelectedProvider(tunisianGroup ? tunisianGroup.id : (voiceData.voice.provider || "11labs"));
                setSelectedVoice(voiceId); setVoiceSpeed([voiceData.voice.speed || 1.0]);
            }
        } catch { toast({ title: "Error", description: "Failed to load voice configuration", variant: "destructive" }); }
        finally { setLoading(false); }
    }, [toast]);

    useEffect(() => { loadData(); }, [loadData]);

    const handleSave = async () => {
        const voice = currentProviderVoices.find(v => v.id === selectedVoice);
        try { setSaving(true); await assistantApi.updateVoice({ provider: voice?.provider || selectedProvider, voice_id: selectedVoice, speed: voiceSpeed[0] }); toast({ title: "Saved", description: "Voice configuration updated" }); }
        catch { toast({ title: "Error", description: "Failed to save", variant: "destructive" }); }
        finally { setSaving(false); }
    };

    const handleLanguageChange = async (option: LanguageOption) => {
        if (option.id === language || switchingTo) return;
        if (!window.confirm(`Switch your AI receptionist to ${option.label}? Its voice, greeting and speech recognition change too. You can switch back at any time.`)) return;
        try {
            setSwitchingTo(option.id);
            await assistantApi.setLanguage(option.id);
            toast({ title: "Language updated", description: `Your assistant now speaks ${option.label}.` });
            await loadData();
        } catch { toast({ title: "Error", description: "Failed to switch language", variant: "destructive" }); }
        finally { setSwitchingTo(null); }
    };

    const currentProviderVoices = providers.find(p => p.id === selectedProvider)?.voices || [];

    if (loading) return <div className="flex items-center justify-center h-96"><Loader2 className="h-8 w-8 animate-spin text-[#0a4c2f]" /></div>;

    return (
        <div>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Voice Configuration</h1>
                    <p className="text-[14px] text-gray-500 font-medium">Configure how your AI assistant sounds.</p>
                </div>
                <div className="flex gap-2">
                    <Link href="/dashboard/voice-agent/control-center" className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-[20px] font-semibold hover:bg-gray-50 transition-colors text-sm shadow-sm">
                        Back to Control Center
                    </Link>
                    <button onClick={handleSave} disabled={saving} className="px-5 py-2.5 bg-gradient-to-b from-[#187848] via-[#0a4c2f] to-[#052b19] text-white rounded-[20px] font-semibold transition-all shadow-[0_4px_16px_rgba(10,76,47,0.3)] flex items-center gap-2 relative overflow-hidden">
                        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white/20 via-transparent to-transparent opacity-50"></div>
                        {saving ? <Loader2 className="w-4 h-4 animate-spin relative z-10" /> : <Save className="w-4 h-4 relative z-10" />}
                        <span className="relative z-10">Save Changes</span>
                    </button>
                </div>
            </div>

            {/* Language */}
            {languages.length > 0 && (
                <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6 mb-6">
                    <h3 className="font-bold text-lg text-gray-900 mb-1">Language</h3>
                    <p className="text-sm text-gray-500 mb-6">The language your assistant speaks on calls. Each language has its own speech recognition, AI model and voices.</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {languages.map((option) => (
                            <button key={option.id} type="button" onClick={() => handleLanguageChange(option)} disabled={switchingTo !== null}
                                className={`p-4 rounded-xl text-left transition-all disabled:cursor-wait ${language === option.id ? "border-2 border-[#0a4c2f] bg-[#0a4c2f]/5 ring-1 ring-[#0a4c2f]/20" : "border border-gray-100 hover:border-[#0a4c2f]/30 bg-gray-50"}`}>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h4 className="font-bold text-gray-900">{option.label}</h4>
                                        {option.native_label !== option.label && <p className="text-sm text-gray-500" dir="auto">{option.native_label}</p>}
                                    </div>
                                    {switchingTo === option.id ? <Loader2 className="h-5 w-5 animate-spin text-[#0a4c2f]" /> : language === option.id && <Check className="h-5 w-5 text-[#0a4c2f]" />}
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <div className="grid gap-6 lg:grid-cols-2">
                {/* Voice Provider */}
                <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                    <h3 className="font-bold text-lg text-gray-900 mb-1">Voice Provider</h3>
                    <p className="text-sm text-gray-500 mb-6">Choose your text-to-speech provider</p>
                    <div className="grid grid-cols-1 gap-3">
                        {providers.map((provider) => (
                            <div key={provider.id} onClick={() => { setSelectedProvider(provider.id); setSelectedVoice(""); }}
                                className={`p-4 rounded-xl cursor-pointer transition-all ${selectedProvider === provider.id ? "border-2 border-[#0a4c2f] bg-[#0a4c2f]/5 ring-1 ring-[#0a4c2f]/20" : "border border-gray-100 hover:border-[#0a4c2f]/30 bg-gray-50"}`}>
                                <div className="flex items-center justify-between">
                                    <div><h4 className="font-bold text-gray-900">{provider.name}</h4><p className="text-sm text-gray-500">{provider.description}</p></div>
                                    {selectedProvider === provider.id && <Check className="h-5 w-5 text-[#0a4c2f]" />}
                                </div>
                                <span className="mt-2 inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 text-gray-600">{provider.voices.length} voices</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Voice Selection */}
                <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                    <h3 className="font-bold text-lg text-gray-900 mb-1">Select Voice</h3>
                    <p className="text-sm text-gray-500 mb-6">Choose a voice for your assistant</p>
                    <div className="grid grid-cols-2 gap-3 max-h-80 overflow-y-auto scrollbar-hide">
                        {currentProviderVoices.map((voice) => (
                            <div key={voice.id} onClick={() => setSelectedVoice(voice.id)}
                                className={`p-3 rounded-xl cursor-pointer transition-all ${selectedVoice === voice.id ? "border-2 border-[#0a4c2f] bg-[#0a4c2f]/5" : "border border-gray-100 hover:border-[#0a4c2f]/30 bg-gray-50"}`}>
                                <div className="flex items-center gap-2"><Volume2 className="h-4 w-4 text-gray-400" /><span className="font-medium text-gray-900">{voice.name}</span></div>
                                <div className="flex gap-1 mt-1">
                                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-gray-100 text-gray-500">{voice.gender}</span>
                                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-gray-100 text-gray-500">{voice.accent}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                    {selectedVoice && (
                        <div className="pt-4 border-t border-gray-100 mt-4">
                            <p className="text-sm text-gray-500">Selected: <span className="font-bold text-gray-900">{currentProviderVoices.find(v => v.id === selectedVoice)?.name}</span></p>
                        </div>
                    )}
                </div>

                {/* Voice Settings */}
                <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6 lg:col-span-2">
                    <h3 className="font-bold text-lg text-gray-900 mb-1">Voice Settings</h3>
                    <p className="text-sm text-gray-500 mb-6">Fine-tune voice parameters</p>
                    <div className="grid gap-6 md:grid-cols-2">
                        <div className="space-y-4">
                            <Label className="font-semibold text-gray-700">Speaking Speed</Label>
                            <div className="flex items-center gap-4">
                                <span className="text-sm text-gray-500 w-12">Slow</span>
                                <Slider value={voiceSpeed} onValueChange={setVoiceSpeed} min={0.5} max={2.0} step={0.1} className="flex-1" />
                                <span className="text-sm text-gray-500 w-12">Fast</span>
                            </div>
                            <p className="text-sm text-gray-400">Current: {voiceSpeed[0].toFixed(1)}x</p>
                        </div>
                        <div className="space-y-4">
                            <Label className="font-semibold text-gray-700">Voice Preview</Label>
                            <textarea value={previewText} onChange={(e) => setPreviewText(e.target.value)} dir="auto" className="w-full p-3 border border-gray-200 rounded-xl resize-none h-20 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30 text-sm" placeholder="Enter text to preview..." />
                            <button className="w-full px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 text-sm">
                                <Play className="w-4 h-4" />Preview Voice (Coming Soon)
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
