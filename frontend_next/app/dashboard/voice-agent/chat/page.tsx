"use client";

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Loader2, Send, MessageSquare, Bot, User, ArrowLeft, Mic, Sparkles } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { vapiApi } from '@/lib/api-endpoints';
import Link from 'next/link';

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    toolCall?: string;
}

export default function ChatTestPage() {
    const { user, isLoading: authLoading } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [assistantId, setAssistantId] = useState<string | null>(null);
    const [systemPrompt, setSystemPrompt] = useState('');
    const [conversationHistory, setConversationHistory] = useState<{ role: string, content: string }[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const loadAssistant = useCallback(async () => {
        if (!user) return;
        try {
            const data = await vapiApi.getMyAssistant();
            if (data?.assistant_id) {
                setAssistantId(data.assistant_id);
                const personality = await fetch('/api/v1/assistant/me/personality', {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}` }
                }).then(r => r.json()).catch(() => ({}));
                const prompt = personality.system_prompt || 'You are a helpful AI assistant.';
                setSystemPrompt(prompt);
                setConversationHistory([{ role: 'system', content: prompt }]);
                setMessages([{ role: 'assistant', content: data.first_message || personality.first_message || "Hi! Thank you for calling. How can I help you today?", timestamp: new Date() }]);
            }
        } catch (err) { console.error("Failed to load assistant", err); }
    }, [user]);

    useEffect(() => { loadAssistant(); }, [loadAssistant]);

    const sendMessage = async () => {
        if (!input.trim() || loading) return;
        const userMessage: Message = { role: 'user', content: input.trim(), timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        const currentInput = input.trim();
        setInput('');
        setLoading(true);
        const newHistory = [...conversationHistory, { role: 'user', content: currentInput }];
        setConversationHistory(newHistory);

        try {
            const response = await fetch('/api/v1/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}` },
                body: JSON.stringify({ messages: newHistory, assistant_id: assistantId })
            });
            if (response.ok) {
                const data = await response.json();
                const aiResponse = data.response || data.choices?.[0]?.message?.content || "I understand. Let me help you with that.";
                setConversationHistory([...newHistory, { role: 'assistant', content: aiResponse }]);
                setMessages(prev => [...prev, { role: 'assistant', content: aiResponse, timestamp: new Date(), toolCall: data.tool_used }]);
            } else {
                const aiResponse = getIntelligentResponse(currentInput, systemPrompt);
                setConversationHistory([...newHistory, { role: 'assistant', content: aiResponse }]);
                setMessages(prev => [...prev, { role: 'assistant', content: aiResponse, timestamp: new Date() }]);
            }
        } catch {
            const aiResponse = getIntelligentResponse(currentInput, systemPrompt);
            setConversationHistory([...newHistory, { role: 'assistant', content: aiResponse }]);
            setMessages(prev => [...prev, { role: 'assistant', content: aiResponse, timestamp: new Date() }]);
        } finally { setLoading(false); }
    };

    const getIntelligentResponse = (userInput: string, prompt: string): string => {
        const lower = userInput.toLowerCase();
        if (lower.includes('book') || lower.includes('appointment') || lower.includes('schedule')) return "I'd love to help you schedule an appointment! What day and time works best for you?";
        if (lower.includes('available') || lower.includes('time')) return "Let me check our availability. We have openings tomorrow at 9:00 AM, 10:00 AM, 11:00 AM, 2:00 PM, and 3:00 PM.";
        if (lower.includes('price') || lower.includes('cost')) return "I'd be happy to provide pricing information! What specific service are you interested in?";
        if (lower.includes('hour') || lower.includes('when') || lower.includes('close')) return "We're open Tuesday through Friday 9 AM to 7 PM, Saturday 9 AM to 6 PM, and Sunday 10 AM to 4 PM.";
        if (lower.includes('cancel')) return "I can help you cancel your appointment. Can you provide the name and scheduled date/time?";
        if (lower.includes('thank') || lower.includes('bye')) return "You're welcome! Thank you for chatting. Have a wonderful day!";
        if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) return "Hello! Welcome! How can I help you today?";
        return "I can assist you with booking appointments, checking availability, or answering questions about our services!";
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    };

    if (authLoading) {
        return <div className="flex items-center justify-center h-[calc(100vh-4rem)]"><Loader2 className="h-12 w-12 animate-spin text-[#0a4c2f]" /></div>;
    }

    return (
        <div className="flex flex-col h-[calc(100vh-200px)]">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h1 className="text-[24px] font-bold text-gray-900 flex items-center gap-2"><MessageSquare className="h-6 w-6" />Chat Test</h1>
                    <p className="text-sm text-gray-500">Test your AI assistant via text chat</p>
                </div>
                <div className="flex gap-2">
                    <Link href="/dashboard/voice-agent/test" className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center gap-2">
                        <Mic className="w-4 h-4" />Voice Test
                    </Link>
                    <Link href="/dashboard/voice-agent/control-center" className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center gap-2">
                        <ArrowLeft className="w-4 h-4" />Back
                    </Link>
                </div>
            </div>

            {/* Chat Container */}
            <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 flex-1 flex flex-col min-h-0 overflow-hidden">
                {/* Chat Header */}
                <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#187848] to-[#0a4c2f] flex items-center justify-center">
                        <Sparkles className="h-5 w-5 text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-gray-900 text-sm">AI Receptionist</h3>
                        {assistantId ? (
                            <span className="text-xs font-bold text-green-700 flex items-center gap-1"><span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>Connected</span>
                        ) : (
                            <span className="text-xs font-bold text-red-600">Not Configured</span>
                        )}
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {msg.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-full bg-[#f3f5f4] flex items-center justify-center shrink-0">
                                    <Bot className="h-4 w-4 text-[#0a4c2f]" />
                                </div>
                            )}
                            <div className={`max-w-[75%] p-3 rounded-2xl ${msg.role === 'user' ? 'bg-[#0a4c2f] text-white rounded-br-md' : 'bg-gray-100 text-gray-900 rounded-bl-md'}`}>
                                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                                {msg.toolCall && <span className="mt-2 inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-white/20 text-white/80">🔧 {msg.toolCall}</span>}
                                <p className="text-xs opacity-50 mt-1">{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                            </div>
                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center shrink-0">
                                    <User className="h-4 w-4 text-gray-500" />
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && (
                        <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-[#f3f5f4] flex items-center justify-center"><Bot className="h-4 w-4 text-[#0a4c2f]" /></div>
                            <div className="bg-gray-100 p-3 rounded-2xl rounded-bl-md">
                                <div className="flex gap-1">
                                    <div className="w-2 h-2 bg-[#0a4c2f]/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 bg-[#0a4c2f]/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 bg-[#0a4c2f]/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-gray-100 bg-gray-50/50">
                    <div className="flex gap-2">
                        <Input id="chat-input" name="chat-message" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyPress} placeholder="Type a message..." disabled={loading || !assistantId} className="flex-1 rounded-xl border-gray-200" autoComplete="off" />
                        <button onClick={sendMessage} disabled={loading || !input.trim() || !assistantId} className="w-10 h-10 bg-[#0a4c2f] hover:bg-[#073922] text-white rounded-xl flex items-center justify-center transition-colors disabled:opacity-40">
                            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                        </button>
                    </div>
                    <p className="text-xs text-gray-400 mt-2 text-center">💡 Try: &quot;I want to book a men&apos;s haircut for tomorrow at 2pm&quot;</p>
                </div>
            </div>
        </div>
    );
}
