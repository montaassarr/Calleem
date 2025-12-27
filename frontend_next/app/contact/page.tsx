import React from 'react';
import Navbar from '@/components/landing/Navbar';
import ContactForm from '@/components/landing/ContactForm';
import FAQ from '@/components/landing/FAQ';
import PreFooterCTA from '@/components/landing/PreFooterCTA';
import Footer from '@/components/landing/Footer';
import ChatWidget from '@/components/landing/ChatWidget';

export default function ContactPage() {
    return (
        <div className="min-h-screen w-full bg-[#648768] overflow-x-hidden font-sans text-white">
            <Navbar />

            <main className="pt-32 md:pt-40 pb-20 px-6 flex flex-col items-center justify-center gap-12" id="contact">
                <div className="w-full max-w-[1200px] flex flex-col items-center justify-center gap-12">

                    {/* Header Section */}
                    <div className="flex flex-col items-center text-center gap-10">

                        <div className="flex flex-col gap-6 items-center">
                            <div className="hidden md:block animate-fade-in-up">
                                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#1c1c1c] bg-transparent shadow-lg backdrop-blur-sm">
                                    <div className="w-1.5 h-1.5 rounded-full bg-[#1e5438] shadow-[0_0_8px_rgba(30,84,56,0.8)]"></div>
                                    <span className="text-[12px] font-medium text-[#184a27] font-manrope">Contact us</span>
                                </div>
                            </div>

                            <h1 className="font-manrope font-bold text-[48px] leading-[1.1] md:text-[56px] text-white">
                                We’re here to help
                            </h1>

                            <p className="text-[18px] md:text-[20px] text-white/65 font-medium max-w-[480px]">
                                Got questions about Calleem or your plans? Send us a message and we’ll reply soon.
                            </p>
                        </div>

                    </div>

                    {/* Form Section */}
                    <div className="w-full flex justify-center">
                        <ContactForm />
                    </div>

                </div>
            </main>

            <FAQ />

            <PreFooterCTA />

            <Footer />
            <ChatWidget />
        </div>
    );
}
