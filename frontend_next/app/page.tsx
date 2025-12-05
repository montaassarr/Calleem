"use client"

import { useEffect } from "react"
import { Header } from "@/components/landing/header"
import Hero from "@/components/landing/hero"
import Features from "@/components/landing/features"
import { TestimonialsSection } from "@/components/landing/testimonials"
import { NewReleasePromo } from "@/components/landing/new-release-promo"
import { FAQSection } from "@/components/landing/faq-section"
import { PricingSection } from "@/components/landing/pricing-section"
import { StickyFooter } from "@/components/landing/sticky-footer"

export default function Home() {
  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove("light", "system")
    root.classList.add("dark")
  }, [])

  return (
    <div className="min-h-screen w-full relative bg-black">
      <Header />

      {/* Hero Section */}
      <Hero />

      {/* Features Section */}
      <div id="features">
        <Features />
      </div>

      {/* Pricing Section */}
      <div id="pricing">
        <PricingSection />
      </div>

      {/* Testimonials Section */}
      <div id="testimonials">
        <TestimonialsSection />
      </div>

      <NewReleasePromo />

      {/* FAQ Section */}
      <div id="faq">
        <FAQSection />
      </div>

      {/* Sticky Footer */}
      <StickyFooter />
    </div>
  )
}
