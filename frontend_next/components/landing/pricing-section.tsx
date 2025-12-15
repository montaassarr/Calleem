"use client"

import { motion } from "framer-motion"
import { Check, Sparkles, Zap, Crown, Building2 } from "lucide-react"
import { useState } from "react"
import { GlassCard } from "@/components/ui/glass-card"

const pricingPlans = [
  {
    name: "Basic",
    monthlyPrice: 149,
    annualPrice: 119,
    description: "Perfect for small businesses getting started with AI",
    features: [
      "500 AI calls per month",
      "Basic appointment booking",
      "Email & chat support",
      "Standard voice options",
      "WhatsApp integration",
      "Basic analytics"
    ],
    popular: false,
    cta: "Start Free Trial",
    icon: Sparkles,
    gradient: "from-blue-500/20 to-cyan-500/20"
  },
  {
    name: "Pro + Smart Automations",
    monthlyPrice: 499,
    annualPrice: 399,
    description: "For growing businesses that need powerful automation",
    features: [
      "Unlimited AI calls",
      "🔥 Smart Automations (built-in)",
      "Google Calendar sync",
      "Airtable data logging",
      "WhatsApp/SMS confirmations",
      "HubSpot CRM integration",
      "Slack notifications",
      "Priority support (24/7)",
      "Custom voice cloning",
      "Advanced analytics",
      "API access"
    ],
    popular: true,
    cta: "Start Free Trial",
    icon: Zap,
    gradient: "from-yellow-500/20 to-orange-500/20"
  },
  {
    name: "Enterprise",
    monthlyPrice: 999,
    annualPrice: 799,
    description: "For agencies and enterprises managing multiple locations",
    features: [
      "Everything in Pro",
      "White-label dashboard",
      "Multi-tenant management",
      "Custom automated workflows",
      "Dedicated account manager",
      "Custom onboarding",
      "SLA guarantees",
      "Advanced security",
      "Custom integrations",
      "Volume discounts"
    ],
    popular: false,
    cta: "Contact Sales",
    icon: Building2,
    gradient: "from-purple-500/20 to-pink-500/20"
  },
]

export function PricingSection() {
  const [isAnnual, setIsAnnual] = useState(false)

  return (
    <section className="relative py-24 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <GlassCard variant="button" className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#0891b2]" />
              <span className="text-sm font-medium text-white/80">Pricing</span>
            </GlassCard>
          </motion.div>

          <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-white via-white to-white/60 bg-clip-text text-transparent mb-4">
            Choose your plan
          </h2>

          <p className="text-lg text-white/60 max-w-2xl mx-auto mb-8">
            Start with a 14-day free trial. No credit card required. Upgrade anytime as your business grows.
          </p>

          {/* Monthly/Annual Toggle */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex items-center justify-center gap-4 p-1 bg-white/5 rounded-full border border-white/10 backdrop-blur-sm w-fit mx-auto"
          >
            <button
              onClick={() => setIsAnnual(false)}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-200 ${!isAnnual ? "bg-[#0891b2] text-white shadow-lg" : "text-white/60 hover:text-white/80"
                }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setIsAnnual(true)}
              className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-200 relative ${isAnnual ? "bg-[#0891b2] text-white shadow-lg" : "text-white/60 hover:text-white/80"
                }`}
            >
              Annual
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                Save 20%
              </span>
            </button>
          </motion.div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {pricingPlans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className={`relative rounded-3xl p-8 backdrop-blur-xl border shadow-2xl transition-all duration-300 ${plan.popular
                ? "bg-gradient-to-br from-slate-950/90 to-slate-900/90 border-yellow-500/50 shadow-yellow-500/20 scale-105"
                : "bg-slate-950/70 border-white/10 hover:border-white/20"
                }`}
            >
              {/* Gradient overlay */}
              <div className={`absolute inset-0 bg-gradient-to-br ${plan.gradient} rounded-3xl pointer-events-none opacity-50`} />

              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                  <div className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-sm font-bold px-6 py-2 rounded-full flex items-center gap-2 shadow-lg">
                    <Crown className="w-4 h-4" />
                    MOST POPULAR
                  </div>
                </div>
              )}

              <div className="relative z-10">
                <div className="text-center mb-8">
                  <div className="flex items-center justify-center mb-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${plan.gradient} flex items-center justify-center`}>
                      <plan.icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center gap-1 mb-2">
                    <span className="text-5xl font-bold text-white">
                      ${isAnnual ? plan.annualPrice : plan.monthlyPrice}
                    </span>
                    <span className="text-white/60 text-lg">/month</span>
                  </div>
                  {isAnnual && (
                    <p className="text-green-400 text-sm font-medium">
                      Save ${(plan.monthlyPrice - plan.annualPrice) * 12}/year
                    </p>
                  )}
                  <p className="text-white/60 text-sm mt-2">{plan.description}</p>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-[#0891b2] flex-shrink-0 mt-0.5" />
                      <span className="text-white/80 text-sm leading-relaxed">{feature}</span>
                    </li>
                  ))}
                </ul>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full py-3 px-6 rounded-lg font-medium transition-all duration-200 ${plan.popular
                    ? "bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg shadow-yellow-500/25 hover:shadow-yellow-500/40"
                    : "bg-white/10 text-white border border-white/20 hover:bg-white/20"
                    }`}
                >
                  {plan.cta}
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-16"
        >
          <p className="text-white/60 mb-4">Need a custom solution? We're here to help.</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="text-[#0891b2] hover:text-[#0891b2]/80 font-medium transition-colors"
          >
            Contact our sales team →
          </motion.button>
        </motion.div>

        {/* Trust Badges */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-16 flex flex-wrap items-center justify-center gap-8 text-white/40 text-sm"
        >
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            14-day free trial
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            No credit card required
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            Cancel anytime
          </div>
        </motion.div>
      </div>
    </section>
  )
}
