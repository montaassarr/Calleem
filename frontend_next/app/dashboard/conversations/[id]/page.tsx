"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, User, Clock, Tag } from "lucide-react"
import { Button } from "@/components/ui/button"
import api from "@/lib/api"
import type { ConversationResponse } from "@/lib/types"
import { useToast } from "@/components/ui/use-toast"

export default function ConversationDetailPage() {
    const params = useParams()
    const router = useRouter()
    const { toast } = useToast()
    const [conversation, setConversation] = useState<ConversationResponse | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchConversation = async () => {
            if (!params.id) return

            try {
                setIsLoading(true)
                const response = await api.get<ConversationResponse>(`/conversations/${params.id}`)
                setConversation(response)
            } catch (error) {
                console.error("Failed to fetch conversation:", error)
                toast({
                    title: "Error",
                    description: "Failed to load conversation details.",
                    variant: "destructive",
                })
            } finally {
                setIsLoading(false)
            }
        }

        fetchConversation()
    }, [params.id, toast])

    const formatDate = (datetime: string) => {
        return new Date(datetime).toLocaleString("en-US", {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        })
    }

    if (isLoading) {
        return (
            <div className="p-6 text-center">
                <p className="text-muted-foreground">Loading conversation...</p>
            </div>
        )
    }

    if (!conversation) {
        return (
            <div className="p-6 text-center">
                <p className="text-muted-foreground">Conversation not found</p>
                <Button variant="outline" className="mt-4" onClick={() => router.back()}>
                    Go Back
                </Button>
            </div>
        )
    }

    const conversationStatus = conversation.state.completed ? "completed" : "active"

    return (
        <div className="p-6 space-y-6 h-[calc(100vh-4rem)] flex flex-col">
            {/* Header */}
            <div className="flex items-center gap-4 border-b pb-4">
                <Button variant="ghost" size="icon" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <div>
                    <h1 className="text-xl font-bold flex items-center gap-2">
                        <User className="h-5 w-5" />
                        {conversation.phone_number}
                    </h1>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                        <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {formatDate(conversation.updated_at)}
                        </span>
                        <span className="flex items-center gap-1">
                            <Tag className="h-3 w-3" />
                            {conversation.state.intent?.replace("_", " ") || "unknown"}
                        </span>
                    </div>
                </div>
                <div className="ml-auto">
                    <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${conversationStatus === "active"
                            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                            : conversationStatus === "completed"
                                ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                                : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
                            }`}
                    >
                        {conversationStatus}
                    </span>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto space-y-4 p-4 rounded-xl border bg-slate-100/10">
                {conversation.messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.role === "client" ? "justify-start" : "justify-end"}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === "client"
                                ? "bg-slate-100 text-foreground rounded-tl-none"
                                : "bg-primary text-primary-foreground rounded-tr-none"
                                }`}
                        >
                            <p className="text-sm">{msg.text}</p>
                            <p className={`text-[10px] mt-1 opacity-70 ${msg.role === "ai" ? "text-primary-foreground" : ""}`}>
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Info Panel */}
            {Object.keys(conversation.state.collected_info || {}).length > 0 && (
                <div className="border-t pt-4">
                    <h3 className="font-medium mb-3">Collected Information</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(conversation.state.collected_info).map(([key, value]) => (
                            value && (
                                <div key={key} className="p-3 rounded-lg border bg-card">
                                    <p className="text-xs text-muted-foreground capitalize mb-1">{key.replace("_", " ")}</p>
                                    <p className="font-medium text-sm truncate">{String(value)}</p>
                                </div>
                            )
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
