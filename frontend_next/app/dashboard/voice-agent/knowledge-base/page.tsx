"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Loader2, Upload, FileText, Trash2, Plus, HelpCircle, Search } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

interface KBDocument {
    id: string;
    vapi_file_id?: string;
    name: string;
    type: string;
    size?: number;
    status: string;
    created_at?: string;
}

interface FAQ {
    question: string;
    answer: string;
}

export default function KnowledgeBasePage() {
    const { toast } = useToast();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [documents, setDocuments] = useState<KBDocument[]>([]);
    const [faqs, setFaqs] = useState<FAQ[]>([{ question: "", answer: "" }]);
    const [savingFaqs, setSavingFaqs] = useState(false);

    useEffect(() => {
        loadDocuments();
    }, []);

    const loadDocuments = async () => {
        try {
            setLoading(true);
            const data = await assistantApi.getKnowledgeBase();
            setDocuments(data.documents || []);
        } catch (error) {
            console.error("Failed to load KB:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            setUploading(true);
            await assistantApi.uploadDocument(file);
            toast({
                title: "Uploaded",
                description: `${file.name} added to knowledge base`
            });
            loadDocuments();
        } catch (error) {
            console.error("Upload failed:", error);
            toast({
                title: "Upload Failed",
                description: "Could not upload document",
                variant: "destructive"
            });
        } finally {
            setUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        }
    };

    const handleDelete = async (docId: string) => {
        try {
            await assistantApi.deleteDocument(docId);
            toast({
                title: "Deleted",
                description: "Document removed from knowledge base"
            });
            setDocuments(documents.filter(d => d.id !== docId));
        } catch (error) {
            console.error("Delete failed:", error);
            toast({
                title: "Error",
                description: "Could not delete document",
                variant: "destructive"
            });
        }
    };

    const addFaqRow = () => {
        setFaqs([...faqs, { question: "", answer: "" }]);
    };

    const updateFaq = (index: number, field: "question" | "answer", value: string) => {
        const newFaqs = [...faqs];
        newFaqs[index][field] = value;
        setFaqs(newFaqs);
    };

    const removeFaq = (index: number) => {
        setFaqs(faqs.filter((_, i) => i !== index));
    };

    const saveFaqs = async () => {
        const validFaqs = faqs.filter(f => f.question.trim() && f.answer.trim());
        if (validFaqs.length === 0) {
            toast({
                title: "No FAQs",
                description: "Please add at least one question and answer",
                variant: "destructive"
            });
            return;
        }

        try {
            setSavingFaqs(true);
            await assistantApi.addFAQs(validFaqs);
            toast({
                title: "Saved",
                description: `${validFaqs.length} FAQ(s) added to knowledge base`
            });
            setFaqs([{ question: "", answer: "" }]);
            loadDocuments();
        } catch (error) {
            console.error("Save FAQs failed:", error);
            toast({
                title: "Error",
                description: "Could not save FAQs",
                variant: "destructive"
            });
        } finally {
            setSavingFaqs(false);
        }
    };

    const formatFileSize = (bytes?: number) => {
        if (!bytes) return "—";
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Knowledge Base</h1>
                    <p className="text-muted-foreground mt-1">
                        Train your AI with documents and FAQs
                    </p>
                </div>
                <Button variant="outline" asChild>
                    <Link href="/dashboard/voice-agent/control-center">Back to Control Center</Link>
                </Button>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                {/* Documents */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <FileText className="h-5 w-5" />
                            Documents
                        </CardTitle>
                        <CardDescription>
                            Upload PDFs, text files, or documents to train your assistant
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {/* Upload Button */}
                        <div className="border-2 border-dashed rounded-lg p-6 text-center">
                            <input
                                ref={fileInputRef}
                                type="file"
                                onChange={handleFileUpload}
                                accept=".pdf,.txt,.doc,.docx,.md"
                                className="hidden"
                                id="file-upload"
                            />
                            <label htmlFor="file-upload" className="cursor-pointer">
                                {uploading ? (
                                    <Loader2 className="h-8 w-8 mx-auto animate-spin text-primary" />
                                ) : (
                                    <Upload className="h-8 w-8 mx-auto text-muted-foreground" />
                                )}
                                <p className="mt-2 font-medium">
                                    {uploading ? "Uploading..." : "Click to upload"}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    PDF, TXT, DOC, DOCX, MD (max 10MB)
                                </p>
                            </label>
                        </div>

                        {/* Document List */}
                        {loading ? (
                            <div className="flex justify-center py-4">
                                <Loader2 className="h-6 w-6 animate-spin" />
                            </div>
                        ) : documents.length === 0 ? (
                            <p className="text-center text-muted-foreground py-4">
                                No documents uploaded yet
                            </p>
                        ) : (
                            <div className="space-y-2">
                                {documents.map((doc) => (
                                    <div
                                        key={doc.id}
                                        className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                                    >
                                        <div className="flex items-center gap-3">
                                            <FileText className="h-4 w-4 text-muted-foreground" />
                                            <div>
                                                <p className="font-medium text-sm">{doc.name}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {formatFileSize(doc.size)} • {doc.status}
                                                </p>
                                            </div>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDelete(doc.id)}
                                        >
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* FAQs */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <HelpCircle className="h-5 w-5" />
                            Frequently Asked Questions
                        </CardTitle>
                        <CardDescription>
                            Add common Q&A pairs for your assistant to reference
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {faqs.map((faq, index) => (
                            <div key={index} className="space-y-2 p-3 border rounded-lg">
                                <div className="flex items-center gap-2">
                                    <Badge variant="secondary">Q{index + 1}</Badge>
                                    <Input
                                        placeholder="Question..."
                                        value={faq.question}
                                        onChange={(e) => updateFaq(index, "question", e.target.value)}
                                    />
                                    {faqs.length > 1 && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => removeFaq(index)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    )}
                                </div>
                                <textarea
                                    placeholder="Answer..."
                                    value={faq.answer}
                                    onChange={(e) => updateFaq(index, "answer", e.target.value)}
                                    className="w-full p-2 border rounded-md text-sm resize-none h-16"
                                />
                            </div>
                        ))}

                        <div className="flex gap-3">
                            <Button variant="outline" onClick={addFaqRow} className="flex-1">
                                <Plus className="h-4 w-4 mr-2" />
                                Add Question
                            </Button>
                            <Button onClick={saveFaqs} disabled={savingFaqs} className="flex-1">
                                {savingFaqs ? (
                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                ) : null}
                                Save FAQs
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
