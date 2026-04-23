"use client";

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Loader2, Upload, FileText, Trash2, Plus, HelpCircle } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

interface KBDocument { id: string; vapi_file_id?: string; name: string; type: string; size?: number; status: string; created_at?: string; }
interface FAQ { question: string; answer: string; }

export default function KnowledgeBasePage() {
    const { toast } = useToast();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [documents, setDocuments] = useState<KBDocument[]>([]);
    const [faqs, setFaqs] = useState<FAQ[]>([{ question: "", answer: "" }]);
    const [savingFaqs, setSavingFaqs] = useState(false);

    useEffect(() => { loadDocuments(); }, []);

    const loadDocuments = async () => {
        try { setLoading(true); const data = await assistantApi.getKnowledgeBase(); setDocuments(data.documents || []); } catch (error) { console.error("Failed to load KB:", error); } finally { setLoading(false); }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]; if (!file) return;
        try { setUploading(true); await assistantApi.uploadDocument(file); toast({ title: "Uploaded", description: `${file.name} added to knowledge base` }); loadDocuments(); }
        catch { toast({ title: "Upload Failed", description: "Could not upload document", variant: "destructive" }); }
        finally { setUploading(false); if (fileInputRef.current) fileInputRef.current.value = ""; }
    };

    const handleDelete = async (docId: string) => {
        try { await assistantApi.deleteDocument(docId); toast({ title: "Deleted", description: "Document removed" }); setDocuments(documents.filter(d => d.id !== docId)); }
        catch { toast({ title: "Error", description: "Could not delete document", variant: "destructive" }); }
    };

    const addFaqRow = () => setFaqs([...faqs, { question: "", answer: "" }]);
    const updateFaq = (i: number, field: "question" | "answer", value: string) => { const n = [...faqs]; n[i][field] = value; setFaqs(n); };
    const removeFaq = (i: number) => setFaqs(faqs.filter((_, idx) => idx !== i));

    const saveFaqs = async () => {
        const valid = faqs.filter(f => f.question.trim() && f.answer.trim());
        if (!valid.length) { toast({ title: "No FAQs", description: "Please add at least one Q&A", variant: "destructive" }); return; }
        try { setSavingFaqs(true); await assistantApi.addFAQs(valid); toast({ title: "Saved", description: `${valid.length} FAQ(s) added` }); setFaqs([{ question: "", answer: "" }]); loadDocuments(); }
        catch { toast({ title: "Error", description: "Could not save FAQs", variant: "destructive" }); }
        finally { setSavingFaqs(false); }
    };

    const formatFileSize = (bytes?: number) => { if (!bytes) return "—"; if (bytes < 1024) return `${bytes} B`; if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`; return `${(bytes / (1024 * 1024)).toFixed(1)} MB`; };

    return (
        <div>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-[32px] font-bold tracking-tight text-gray-900 mb-1 leading-none">Knowledge Base</h1>
                    <p className="text-[14px] text-gray-500 font-medium">Train your AI with documents and FAQs.</p>
                </div>
                <Link href="/dashboard/voice-agent/control-center" className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-[20px] font-semibold hover:bg-gray-50 transition-colors text-sm shadow-sm">
                    Back to Control Center
                </Link>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                {/* Documents */}
                <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                    <h3 className="font-bold text-lg text-gray-900 mb-1 flex items-center gap-2"><FileText className="h-5 w-5" />Documents</h3>
                    <p className="text-sm text-gray-500 mb-6">Upload PDFs, text files, or documents to train your assistant</p>

                    <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 text-center mb-4 hover:border-[#0a4c2f]/30 transition-colors">
                        <input ref={fileInputRef} type="file" onChange={handleFileUpload} accept=".pdf,.txt,.doc,.docx,.md" className="hidden" id="file-upload" />
                        <label htmlFor="file-upload" className="cursor-pointer">
                            {uploading ? <Loader2 className="h-8 w-8 mx-auto animate-spin text-[#0a4c2f]" /> : <Upload className="h-8 w-8 mx-auto text-gray-400" />}
                            <p className="mt-2 font-medium text-gray-900">{uploading ? "Uploading..." : "Click to upload"}</p>
                            <p className="text-sm text-gray-500">PDF, TXT, DOC, DOCX, MD (max 10MB)</p>
                        </label>
                    </div>

                    {loading ? (
                        <div className="flex justify-center py-4"><Loader2 className="h-6 w-6 animate-spin text-[#0a4c2f]" /></div>
                    ) : documents.length === 0 ? (
                        <p className="text-center text-gray-500 py-4">No documents uploaded yet</p>
                    ) : (
                        <div className="space-y-2">
                            {documents.map((doc) => (
                                <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                                    <div className="flex items-center gap-3">
                                        <FileText className="h-4 w-4 text-gray-400" />
                                        <div>
                                            <p className="font-medium text-sm text-gray-900">{doc.name}</p>
                                            <p className="text-xs text-gray-500">{formatFileSize(doc.size)} • {doc.status}</p>
                                        </div>
                                    </div>
                                    <button onClick={() => handleDelete(doc.id)} className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* FAQs */}
                <div className="bg-white rounded-[24px] shadow-[0_2px_15px_-4px_rgba(0,0,0,0.03)] border border-gray-100 p-6">
                    <h3 className="font-bold text-lg text-gray-900 mb-1 flex items-center gap-2"><HelpCircle className="h-5 w-5" />Frequently Asked Questions</h3>
                    <p className="text-sm text-gray-500 mb-6">Add common Q&A pairs for your assistant</p>

                    <div className="space-y-4">
                        {faqs.map((faq, index) => (
                            <div key={index} className="space-y-2 p-3 border border-gray-100 rounded-xl">
                                <div className="flex items-center gap-2">
                                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 text-gray-600">Q{index + 1}</span>
                                    <Input placeholder="Question..." value={faq.question} onChange={(e) => updateFaq(index, "question", e.target.value)} className="rounded-lg border-gray-200" />
                                    {faqs.length > 1 && (
                                        <button onClick={() => removeFaq(index)} className="p-2 text-gray-400 hover:text-red-500 rounded-lg"><Trash2 className="h-4 w-4" /></button>
                                    )}
                                </div>
                                <textarea placeholder="Answer..." value={faq.answer} onChange={(e) => updateFaq(index, "answer", e.target.value)} className="w-full p-2 border border-gray-200 rounded-lg text-sm resize-none h-16 focus:outline-none focus:ring-2 focus:ring-[#0a4c2f]/20 focus:border-[#0a4c2f]/30" />
                            </div>
                        ))}

                        <div className="flex gap-3">
                            <button onClick={addFaqRow} className="flex-1 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors text-sm flex items-center justify-center gap-2">
                                <Plus className="h-4 w-4" />Add Question
                            </button>
                            <button onClick={saveFaqs} disabled={savingFaqs} className="flex-1 px-4 py-2.5 bg-[#0a4c2f] hover:bg-[#073922] text-white rounded-xl font-medium transition-colors text-sm flex items-center justify-center gap-2">
                                {savingFaqs && <Loader2 className="h-4 w-4 animate-spin" />}Save FAQs
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
