"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, MessageSquare, User, Clock } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { conversationsApi } from "@/lib/api-endpoints";
import { useRouter } from "next/navigation";
import type { ConversationResponse } from "@/lib/types";

export default function ConversationsPage() {
    const router = useRouter();
    const [searchTerm, setSearchTerm] = useState("");

    const { data: conversations = [], isLoading } = useQuery({
        queryKey: ["conversations", searchTerm],
        queryFn: () => conversationsApi.list({ search: searchTerm, limit: 100 }),
    });

    const formatDate = (datetime: string) => {
        const date = new Date(datetime);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        } else if (days === 1) {
            return 'Yesterday';
        } else if (days < 7) {
            return `${days} days ago`;
        } else {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
    };

    const getIntentColor = (intent: string) => {
        switch (intent) {
            case 'book_appointment':
                return 'bg-blue-100 text-blue-700 border-blue-200';
            case 'cancel_appointment':
                return 'bg-red-100 text-red-700 border-red-200';
            case 'greeting':
                return 'bg-green-100 text-green-700 border-green-200';
            case 'service_info':
                return 'bg-purple-100 text-purple-700 border-purple-200';
            default:
                return 'bg-gray-100 text-gray-700 border-gray-200';
        }
    };

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Conversations</h1>
                    <p className="text-muted-foreground">View AI chat history and customer interactions</p>
                </div>
            </div>

            {/* Search */}
            <div className="glass rounded-2xl p-4 mb-6">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                        placeholder="Search by phone number..."
                        className="pl-10 glass-strong"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* Conversations List */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {isLoading ? (
                    <div className="col-span-2 glass rounded-2xl p-8 text-center">
                        <p className="text-muted-foreground">Loading conversations...</p>
                    </div>
                ) : conversations.length === 0 ? (
                    <div className="col-span-2 glass rounded-2xl p-8 text-center">
                        <MessageSquare className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                        <p className="text-muted-foreground">No conversations yet</p>
                        <p className="text-sm text-muted-foreground mt-2">
                            Conversations will appear here when customers chat with your AI receptionist
                        </p>
                    </div>
                ) : (
                    conversations.map((conversation: ConversationResponse) => {
                        const lastMessage = conversation.messages[conversation.messages.length - 1];
                        const messageCount = conversation.messages.length;

                        return (
                            <div
                                key={conversation.id}
                                className="glass rounded-2xl p-4 hover:shadow-lg transition-all cursor-pointer"
                                onClick={() => router.push(`/dashboard/conversations/${conversation.id}`)}
                            >
                                {/* Header */}
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                                            <User className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <p className="font-medium">{conversation.phone_number}</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <Clock className="w-3 h-3 text-muted-foreground" />
                                                <span className="text-xs text-muted-foreground">
                                                    {formatDate(conversation.updated_at)}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getIntentColor(conversation.state.intent)}`}>
                                        {conversation.state.intent?.replace('_', ' ') || 'unknown'}
                                    </span>
                                </div>

                                {/* Last Message */}
                                <div className="glass-strong rounded-lg p-3 mb-3">
                                    <p className="text-sm text-muted-foreground mb-1">
                                        {lastMessage?.role === 'client' ? 'Customer:' : 'AI:'}
                                    </p>
                                    <p className="text-sm line-clamp-2">{lastMessage?.text}</p>
                                </div>

                                {/* Footer */}
                                <div className="flex items-center justify-between text-xs text-muted-foreground">
                                    <span>{messageCount} messages</span>
                                    <span className={`px-2 py-1 rounded-full border ${conversation.status === 'active' ? 'bg-green-100 text-green-700 border-green-200' :
                                            conversation.status === 'completed' ? 'bg-blue-100 text-blue-700 border-blue-200' :
                                                'bg-gray-100 text-gray-700 border-gray-200'
                                        }`}>
                                        {conversation.status || 'active'}
                                    </span>
                                </div>

                                {/* Collected Info */}
                                {conversation.state.collected_info && Object.keys(conversation.state.collected_info).length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-white/10">
                                        <p className="text-xs text-muted-foreground mb-2">Collected Info:</p>
                                        <div className="flex flex-wrap gap-2">
                                            {Object.entries(conversation.state.collected_info).map(([key, value]) => (
                                                value && (
                                                    <span key={key} className="text-xs bg-white/10 px-2 py-1 rounded">
                                                        {key}: {String(value)}
                                                    </span>
                                                )
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
