"use client";

import { useState, useEffect } from "react";
import { Loader2, Trash2, Plus, HelpCircle } from "lucide-react";
import { assistantApi } from "@/lib/api-endpoints";
import { useToast } from "@/hooks/use-toast";
import Link from "next/link";

interface FAQ { question: string; answer: string; }

export default function KnowledgeBasePage() {
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [faqs, setFaqs] = useState<FAQ[]>([{ question: "", answer: "" }]);
    const [savingFaqs, setSavingFaqs] = useState(false);

    useEffect(() => {
        loadFaqs();
    }, []);

    const loadFaqs = async () => {
        try { 
            setLoading(true); 
            const data = await assistantApi.getKnowledgeBase(); 
            if (data.faqs && data.faqs.length > 0) {
                setFaqs(data.faqs);
            } else {
                setFaqs([{ question: "", answer: "" }]);
            }
        } catch (error) { 
            console.error("Failed to load KB:", error); 
        } finally { 
            setLoading(false); 
        }
    };

    const addFaqRow = () => setFaqs([...faqs, { question: "", answer: "" }]);
    const updateFaq = (i: number, field: "question" | "answer", value: string) => { const n = [...faqs]; n[i][field] = value; setFaqs(n); };
    const removeFaq = (i: number) => setFaqs(faqs.filter((_, idx) => idx !== i));

    const saveFaqs = async () => {
        const valid = faqs.filter(f => f.question.trim() && f.answer.trim());
        if (!valid.length) { toast({ title: "No FAQs", description: "Please add at least one Q&A", variant: "destructive" }); return; }
        try { setSavingFaqs(true); await assistantApi.addFAQs(valid); toast({ title: "Saved", description: `${valid.length} FAQ(s) added` }); loadFaqs(); }
        catch { toast({ title: "Error", description: "Could not save FAQs", variant: "destructive" }); }
        finally { setSavingFaqs(false); }
    };

    return (
        <div className="max-w-7xl mx-auto pb-12">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-4">
                <div className="space-y-1">
                    <h1 className="text-4xl font-black tracking-tight text-slate-900 leading-none">Knowledge Base</h1>
                    <p className="text-slate-500 font-medium">Train your AI with documents and FAQs.</p>
                </div>
                <Link href="/dashboard/voice-agent/control-center" className="py-3 px-6 bg-white border border-slate-200 text-slate-700 rounded-2xl font-bold hover:bg-slate-50 transition-colors shadow-sm">
                    Back to Control Center
                </Link>
            </div>

            <div className="flex justify-center">
                {/* FAQs Card */}
                <div className="group relative bg-white rounded-[2.5rem] shadow-sm border border-slate-100 p-8 overflow-hidden h-fit w-full max-w-3xl">
                    <div className="absolute top-0 inset-x-0 h-2 bg-gradient-to-r from-[#064e3b] to-emerald-500 opacity-90" />
                    
                    <div className="mb-8">
                        <h3 className="text-2xl font-black text-slate-900 flex items-center gap-2 mb-1">
                            <HelpCircle className="h-6 w-6 text-[#064e3b]" />
                            Frequently Asked Questions
                        </h3>
                        <p className="text-sm font-medium text-slate-500">Add common Q&A pairs for your assistant.</p>
                    </div>

                    {loading ? (
                        <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-[#064e3b]" /></div>
                    ) : (
                        <div className="space-y-4">
                            {faqs.map((faq, index) => (
                                <div key={index} className="space-y-3 p-5 bg-slate-50/50 border border-slate-100 rounded-[1.5rem]">
                                    <div className="flex items-center gap-3">
                                        <span className="px-3 py-1 rounded-xl text-xs font-black bg-[#064e3b]/10 text-[#064e3b]">Q{index + 1}</span>
                                        <input 
                                            placeholder="Question..." 
                                            value={faq.question} 
                                            onChange={(e) => updateFaq(index, "question", e.target.value)} 
                                            className="w-full px-4 py-3 bg-white border border-slate-200/60 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-[#064e3b]/10 focus:border-[#064e3b] transition-all shadow-sm" 
                                        />
                                        {faqs.length > 1 && (
                                            <button onClick={() => removeFaq(index)} className="p-3 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-colors shrink-0 shadow-sm border border-transparent hover:border-red-100 bg-white">
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        )}
                                    </div>
                                    <textarea 
                                        placeholder="Answer..." 
                                        value={faq.answer} 
                                        onChange={(e) => updateFaq(index, "answer", e.target.value)} 
                                        className="w-full px-4 py-3 bg-white border border-slate-200/60 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-[#064e3b]/10 focus:border-[#064e3b] transition-all shadow-sm resize-none h-24" 
                                    />
                                </div>
                            ))}

                            <div className="flex gap-3 mt-6">
                                <button onClick={addFaqRow} className="flex-1 py-3.5 px-6 rounded-2xl font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors duration-300 flex items-center justify-center gap-2">
                                    <Plus className="h-5 w-5" /> Add Question
                                </button>
                                <button onClick={saveFaqs} disabled={savingFaqs} className="flex-1 bg-[#064e3b] hover:bg-[#064e3b]/90 text-white font-bold py-3.5 px-6 rounded-2xl transition-all duration-300 active:scale-[0.98] flex items-center justify-center gap-2 shadow-lg shadow-[#064e3b]/20 disabled:opacity-50">
                                    {savingFaqs && <Loader2 className="w-4 h-4 animate-spin" />} Save FAQs
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
