import React from 'react';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import { INDUSTRIES } from '@/lib/industry-data';
import Navbar from '@/components/landing/Navbar';
import Footer from '@/components/landing/Footer';
import PreFooterCTA from '@/components/landing/PreFooterCTA';
import { Check, X, ArrowRight } from 'lucide-react';

interface Props {
    params: {
        industry: string;
    };
}

// 1. Generate Static Params for Build Time Performance
export async function generateStaticParams() {
    return INDUSTRIES.map((industry) => ({
        industry: industry.slug,
    }));
}

// 2. Dynamic Metadata for SEO
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const industryData = INDUSTRIES.find((i) => i.slug === params.industry);

    if (!industryData) {
        return {
            title: 'Industry Not Found',
        };
    }

    return {
        title: industryData.title,
        description: industryData.description,
        keywords: industryData.keywords,
        openGraph: {
            title: industryData.title,
            description: industryData.description,
            type: 'website',
        },
    };
}

// 3. Page Component
export default function IndustryPage({ params }: Props) {
    const data = INDUSTRIES.find((i) => i.slug === params.industry);

    if (!data) {
        notFound();
    }

    const jsonLd = {
        '@context': 'https://schema.org',
        '@type': data.schemaType,
        name: data.name,
        description: data.description,
        image: 'https://calleem.tech/og-image.png',
    };

    return (
        <main className="min-h-screen bg-[#0a0a0a] text-white selection:bg-[#2C7A44] selection:text-white">
            <script
                type="application/ld-json"
                dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
            />

            <Navbar />

            {/* Hero Section */}
            <section className="relative pt-32 pb-20 px-6 md:px-10 overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-[600px] bg-gradient-to-b from-[#153629] to-transparent opacity-40 z-0 pointer-events-none" />

                <div className="max-w-[1200px] mx-auto relative z-10 flex flex-col items-center text-center gap-8">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#2C7A44]/10 border border-[#2C7A44]/20 text-[#2C7A44] text-sm font-semibold tracking-wide uppercase">
                        <span className="w-2 h-2 rounded-full bg-[#2C7A44] animate-pulse" />
                        For {data.name}
                    </div>

                    <h1 className="font-host font-bold text-4xl md:text-6xl lg:text-7xl leading-[1.1] max-w-[900px]">
                        {data.title}
                    </h1>

                    <p className="font-manrope text-lg md:text-xl text-white/60 max-w-[600px] leading-relaxed">
                        {data.description}
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 mt-4">
                        <a
                            href="/contact"
                            className="px-8 py-4 bg-[#2C7A44] hover:bg-[#236336] text-white rounded-full font-bold text-lg transition-all shadow-[0_0_20px_rgba(44,122,68,0.3)] hover:shadow-[0_0_30px_rgba(44,122,68,0.5)] flex items-center justify-center gap-2 group"
                        >
                            Get Started
                            <ArrowRight size={18} className="-rotate-45 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                        </a>
                    </div>
                </div>
            </section>

            {/* Pain Points Section */}
            <section className="py-20 px-6 md:px-10 bg-[#0e0e0e]">
                <div className="max-w-[1100px] mx-auto">
                    <div className="flex flex-col md:flex-row gap-12 items-center">
                        <div className="flex-1 space-y-6">
                            <h2 className="font-host font-bold text-3xl md:text-4xl leading-tight">
                                Stop losing business to <span className="text-red-400">missed calls</span>.
                            </h2>
                            <p className="text-white/60 text-lg">
                                In the {data.name} industry, every missed call is a missed opportunity.
                                Traditional voicemail just doesn't cut it anymore.
                            </p>
                        </div>

                        <div className="flex-1 grid gap-4 w-full">
                            {data.painPoints.map((point, i) => (
                                <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-[#1c1c1c] border border-white/5">
                                    <div className="p-2 rounded-full bg-red-500/10 text-red-400 shrink-0">
                                        <X size={20} />
                                    </div>
                                    <span className="font-medium text-white/80">{point}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Benefits / Solution Section */}
            <section className="py-24 px-6 md:px-10 bg-[#153629] relative overflow-hidden">
                {/* Background Pattern */}
                <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>

                <div className="max-w-[1100px] mx-auto relative z-10">
                    <div className="text-center mb-16">
                        <h2 className="font-host font-bold text-3xl md:text-5xl mb-6">
                            Why {data.name} choose Calleem
                        </h2>
                        <p className="text-white/60 text-lg max-w-[600px] mx-auto">
                            We understand the unique challenges of your business. That's why we built an AI receptionist specifically for you.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        {data.benefits.map((benefit, i) => (
                            <div key={i} className="p-8 rounded-[30px] bg-[#0e2e22] border border-white/10 hover:border-[#2C7A44]/50 transition-colors group">
                                <div className="w-12 h-12 rounded-full bg-[#2C7A44]/20 flex items-center justify-center text-[#2C7A44] mb-6 group-hover:scale-110 transition-transform">
                                    <Check size={24} strokeWidth={3} />
                                </div>
                                <h3 className="font-bold text-xl mb-3">{benefit}</h3>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <PreFooterCTA />
            <Footer />
        </main>
    );
}
