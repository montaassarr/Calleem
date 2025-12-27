import React from 'react';
import Navbar from '@/components/landing/Navbar';
import Hero from '@/components/landing/Hero';
import HowItWorks from '@/components/landing/HowItWorks';
import BentoGrid from '@/components/landing/BentoGrid';
import Comparison from '@/components/landing/Comparison';
import Pricing from '@/components/landing/Pricing';
import FAQ from '@/components/landing/FAQ';
import PreFooterCTA from '@/components/landing/PreFooterCTA';
import Footer from '@/components/landing/Footer';
import ChatWidget from '@/components/landing/ChatWidget';


export default function Home() {
  return (
    <div className="flex flex-col w-full min-h-screen bg-[#648768] text-white selection:bg-lime selection:text-forest relative">
      <Navbar />
      <main className="flex-grow">
        <Hero />
        <HowItWorks />
        <BentoGrid />
        <Comparison />
        <Pricing />
        <FAQ />
        <PreFooterCTA />

      </main>
      <Footer />
      <ChatWidget />
    </div>
  );
}
