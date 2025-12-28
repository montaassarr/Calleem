"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { DataTable } from '@/components/admin/DataTable';
import { CrudModal } from '@/components/admin/CrudModal';
import { DeleteDialog } from '@/components/admin/DeleteDialog';
import { adminApi, Conversation } from '@/lib/api/admin';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageSquare } from 'lucide-react';

export default function ConversationsPage() {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [pageSize] = useState(10);
    const [phoneFilter, setPhoneFilter] = useState('');

    // Modal states
    const [isViewOpen, setIsViewOpen] = useState(false);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [selectedConv, setSelectedConv] = useState<Conversation | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { toast } = useToast();

    const fetchConversations = useCallback(async () => {
        try {
            setLoading(true);
            const data = await adminApi.getConversations((page - 1) * pageSize, pageSize, phoneFilter);

            if (Array.isArray(data)) {
                setConversations(data);
                setTotal(data.length);
            } else {
                setConversations(data.items || []);
                setTotal(data.total || 0);
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch conversations",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    }, [page, pageSize, phoneFilter, toast]);

    useEffect(() => {
        fetchConversations();
    }, [fetchConversations]);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            if (phoneFilter) fetchConversations();
        }, 500);
        return () => clearTimeout(timer);
    }, [phoneFilter, fetchConversations]);

    const handleView = (conv: Conversation) => {
        setSelectedConv(conv);
        setIsViewOpen(true);
    };

    const handleDeleteClick = (conv: Conversation) => {
        setSelectedConv(conv);
        setIsDeleteOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!selectedConv) return;
        try {
            setIsSubmitting(true);
            await adminApi.deleteConversation(selectedConv.id);
            toast({ title: "Success", description: "Conversation deleted successfully" });
            setIsDeleteOpen(false);
            fetchConversations();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to delete conversation",
                variant: "destructive"
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const columns = [
        { key: 'phone_number', label: 'Phone Number' },
        {
            key: 'updated_at',
            label: 'Last Active',
            render: (date: string) => new Date(date).toLocaleString()
        },
        {
            key: 'messages',
            label: 'Messages',
            render: (msgs: any[]) => (
                <Badge variant="secondary">
                    {msgs?.length || 0} msgs
                </Badge>
            )
        },
        {
            key: 'state',
            label: 'Intent',
            render: (state: any) => (
                <Badge variant="outline">
                    {state?.intent || 'Unknown'}
                </Badge>
            )
        },
        {
            key: 'actions',
            label: 'View',
            render: (_value: unknown, row: Conversation) => (
                <Button variant="ghost" size="sm" onClick={() => handleView(row)}>
                    <MessageSquare className="h-4 w-4 mr-2" /> View
                </Button>
            )
        }
    ];

    return (
        <div className="p-6">
            <DataTable
                title="Conversations"
                columns={columns}
                data={conversations}
                total={total}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
                onSearch={setPhoneFilter}
                searchPlaceholder="Search by phone..."
                onDelete={handleDeleteClick}
                isLoading={loading}
            />

            <CrudModal
                open={isViewOpen}
                onOpenChange={setIsViewOpen}
                title={`Conversation with ${selectedConv?.phone_number}`}
            >
                <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                    <div className="space-y-4">
                        {selectedConv?.messages?.map((msg, i) => (
                            <div
                                key={i}
                                className={`flex flex-col ${msg.role === 'client' ? 'items-end' : 'items-start'
                                    }`}
                            >
                                <div
                                    className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'client'
                                        ? 'bg-primary text-primary-foreground'
                                        : 'bg-muted'
                                        }`}
                                >
                                    <p className="text-sm">{msg.text}</p>
                                </div>
                                <span className="text-xs text-muted-foreground mt-1">
                                    {new Date(msg.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                        ))}
                        {(!selectedConv?.messages || selectedConv.messages.length === 0) && (
                            <div className="text-center text-muted-foreground py-8">
                                No messages in this conversation.
                            </div>
                        )}
                    </div>
                </ScrollArea>
                <div className="mt-4 border-t pt-4">
                    <h4 className="font-semibold mb-2">Current State</h4>
                    <pre className="bg-muted p-2 rounded-md text-xs overflow-auto">
                        {JSON.stringify(selectedConv?.state, null, 2)}
                    </pre>
                </div>
            </CrudModal>

            <DeleteDialog
                open={isDeleteOpen}
                onOpenChange={setIsDeleteOpen}
                onConfirm={handleDeleteConfirm}
                title="Delete Conversation"
                description="Are you sure you want to delete this conversation history?"
                isLoading={isSubmitting}
            />
        </div>
    );
}
