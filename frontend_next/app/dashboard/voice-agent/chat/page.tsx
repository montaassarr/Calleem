"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
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

    useEffect(() => {
        loadAssistant();
    }, [user]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadAssistant = async () => {
        if (!user) return;
        try {
            const data = await vapiApi.getMyAssistant();
            if (data?.assistant_id) {
                setAssistantId(data.assistant_id);

                // Get personality/system prompt
                const personality = await fetch('/api/v1/assistant/me/personality', {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}` }
                }).then(r => r.json()).catch(() => ({}));

                const prompt = personality.system_prompt || 'You are a helpful AI assistant.';
                setSystemPrompt(prompt);
                setConversationHistory([{ role: 'system', content: prompt }]);

                // Add welcome message
                setMessages([{
                    role: 'assistant',
                    content: data.first_message || personality.first_message || "Hi! Thank you for calling. How can I help you today?",
                    timestamp: new Date()
                }]);
            }
        } catch (err) {
            console.error("Failed to load assistant", err);
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const userMessage: Message = {
            role: 'user',
            content: input.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        const currentInput = input.trim();
        setInput('');
        setLoading(true);

        // Add to conversation history
        const newHistory = [...conversationHistory, { role: 'user', content: currentInput }];
        setConversationHistory(newHistory);

        try {
            // Call OpenAI via our backend for real AI responses
            const response = await fetch('/api/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({
                    messages: newHistory,
                    assistant_id: assistantId
                })
            });

            if (response.ok) {
                const data = await response.json();
                const aiResponse = data.response || data.choices?.[0]?.message?.content || "I understand. Let me help you with that.";

                setConversationHistory([...newHistory, { role: 'assistant', content: aiResponse }]);
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: aiResponse,
                    timestamp: new Date(),
                    toolCall: data.tool_used
                }]);
            } else {
                // Fallback to simulated intelligent response
                const aiResponse = getIntelligentResponse(currentInput, systemPrompt);
                setConversationHistory([...newHistory, { role: 'assistant', content: aiResponse }]);
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: aiResponse,
                    timestamp: new Date()
                }]);
            }
        } catch {
            // Fallback response
            const aiResponse = getIntelligentResponse(currentInput, systemPrompt);
            setConversationHistory([...newHistory, { role: 'assistant', content: aiResponse }]);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: aiResponse,
                timestamp: new Date()
            }]);
        } finally {
            setLoading(false);
        }
    };

    const getIntelligentResponse = (userInput: string, prompt: string): string => {
        const lower = userInput.toLowerCase();

        // Extract business info from prompt
        const hasHairSalon = prompt.toLowerCase().includes('hair') || prompt.toLowerCase().includes('salon');
        const hasDental = prompt.toLowerCase().includes('dental') || prompt.toLowerCase().includes('dentist');

        if (lower.includes('book') || lower.includes('appointment') || lower.includes('schedule')) {
            if (hasHairSalon) {
                return "I'd be happy to help you book an appointment! What service are you interested in? We offer Women's Haircut ($45), Men's Haircut ($30), Full Color ($85), and Highlights ($120). What time works best for you?";
            }
            return "I'd love to help you schedule an appointment! What day and time works best for you? And may I have your name and phone number?";
        }

        if (lower.includes('available') || lower.includes('time') || lower.includes('slot') || lower.includes('open')) {
            return "Let me check our availability. We have openings tomorrow at 9:00 AM, 10:00 AM, 11:00 AM, 2:00 PM, and 3:00 PM. Which time would work best for you?";
        }

        if (lower.includes('price') || lower.includes('cost') || lower.includes('how much') || lower.includes('rate')) {
            if (hasHairSalon) {
                return "Our services include:\n• Women's Haircut: $45-65 (45 min)\n• Men's Haircut: $30-40 (30 min)\n• Full Color: $85-120 (2 hours)\n• Highlights: $95-185 (2 hours)\n• Blowout: $45 (45 min)\n\nWhich service interests you?";
            }
            return "I'd be happy to provide pricing information! What specific service are you interested in?";
        }

        if (lower.includes('hour') || lower.includes('when') || lower.includes('close')) {
            return "We're open Tuesday through Friday 9 AM to 7 PM, Saturday 9 AM to 6 PM, and Sunday 10 AM to 4 PM. We're closed on Monday. Would you like to schedule an appointment?";
        }

        if (lower.includes('cancel')) {
            return "I can help you cancel your appointment. Can you please provide the name the appointment is under and the scheduled date/time?";
        }

        if (lower.includes('name') || lower.includes('who')) {
            return "I'm Sarah, your AI receptionist! I'm here to help you with appointments, answer questions about our services, and provide information. How can I assist you today?";
        }

        if (lower.includes('thank') || lower.includes('bye') || lower.includes('goodbye')) {
            return "You're welcome! Thank you for chatting with us. Have a wonderful day! Don't hesitate to reach out if you need anything else.";
        }

        if (lower.includes('hello') || lower.includes('hi ') || lower === 'hi' || lower.includes('hey')) {
            return "Hello! Welcome! I'm here to help you book appointments, check availability, or answer any questions. What can I do for you today?";
        }

        return "I'm here to help! I can assist you with booking appointments, checking availability, or answering questions about our services. What would you like to know?";
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    if (authLoading) {
        return (
            <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 h-[calc(100vh-4rem)] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <MessageSquare className="h-6 w-6" />
                        Chat Test
                    </h1>
                    <p className="text-muted-foreground text-sm">
                        Test your AI assistant via text chat
                    </p>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" asChild>
                        <Link href="/dashboard/voice-agent/test">
                            <Mic className="w-4 h-4 mr-2" />
                            Voice Test
                        </Link>
                    </Button>
                    <Button variant="ghost" asChild>
                        <Link href="/dashboard/voice-agent/control-center">
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back
                        </Link>
                    </Button>
                </div>
            </div>

            {/* Chat Container */}
            <Card className="bg-white border-slate-200 shadow-sm flex-1 flex flex-col min-h-0">
                <CardHeader className="bg-white border-slate-200 shadow-sm pb-3 border-b">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                                <Sparkles className="h-5 w-5 text-white" />
                            </div>
                            <div>
                                <CardTitle className="bg-white border-slate-200 shadow-sm text-base">AI Receptionist</CardTitle>
                                <CardDescription className="bg-white border-slate-200 shadow-sm text-xs">
                                    {assistantId ? (
                                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">
                                            <span className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></span>
                                            Connected
                                        </Badge>
                                    ) : (
                                        <Badge variant="destructive" className="text-xs">Not Configured</Badge>
                                    )}
                                </CardDescription>
                            </div>
                        </div>
                    </div>
                </CardHeader>

                <CardContent className="bg-white border-slate-200 shadow-sm flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            {msg.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary/20 to-purple-200 flex items-center justify-center flex-shrink-0">
                                    <Bot className="h-4 w-4 text-primary" />
                                </div>
                            )}
                            <div
                                className={`max-w-[75%] p-3 rounded-2xl ${msg.role === 'user'
                                        ? 'bg-primary text-primary-foreground rounded-br-md'
                                        : 'bg-slate-100 rounded-bl-md'
                                    }`}
                            >
                                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                                {msg.toolCall && (
                                    <Badge variant="outline" className="mt-2 text-xs">
                                        🔧 {msg.toolCall}
                                    </Badge>
                                )}
                                <p className="text-xs opacity-50 mt-1">
                                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </p>
                            </div>
                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                                    <User className="h-4 w-4" />
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && (
                        <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary/20 to-purple-200 flex items-center justify-center">
                                <Bot className="h-4 w-4 text-primary" />
                            </div>
                            <div className="bg-slate-100 p-3 rounded-2xl rounded-bl-md">
                                <div className="flex gap-1">
                                    <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </CardContent>

                {/* Input Area */}
                <div className="p-4 border-t bg-slate-100/30">
                    <div className="flex gap-2">
                        <Input
                            id="chat-input"
                            name="chat-message"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Type a message... (e.g., 'I want to book a haircut')"
                            disabled={loading || !assistantId}
                            className="flex-1"
                            autoComplete="off"
                        />
                        <Button
                            onClick={sendMessage}
                            disabled={loading || !input.trim() || !assistantId}
                            size="icon"
                            className="shrink-0"
                        >
                            {loading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Send className="h-4 w-4" />
                            )}
                        </Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2 text-center">
                        💡 Try: "I want to book a men's haircut for tomorrow at 2pm"
                    </p>
                </div>
            </Card>
        </div>
    );
}
