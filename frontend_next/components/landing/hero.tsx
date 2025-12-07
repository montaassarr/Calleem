"use client"

import { geist } from "@/lib/fonts"
import { cn } from "@/lib/utils"
import { Phone, Calendar, MessageSquare, Bot, MoveRight, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import Link from "next/link"
import ScrollingLogos from "@/components/ui/scrolling-logos"
import { sampleLogos } from "@/lib/sample-logos"

export default function Hero() {
  return (
    <div id="hero-section" className="bg-background relative min-h-screen w-full overflow-x-hidden py-20 md:py-32 md:px-6">
      {/* Gradient orbs for visual appeal */}
      <div className="absolute top-20 right-10 w-72 h-72 bg-rose-500/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-20 left-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-radial from-primary/5 to-transparent rounded-full blur-3xl pointer-events-none" />

      <div className="container mx-auto px-4 2xl:max-w-[1400px] relative z-10">
        {/* Badge */}
        <motion.div
          className="flex justify-center"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.1 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-medium backdrop-blur-sm">
            <Sparkles className="w-4 h-4" />
            <span>AI-Powered Receptionist Platform</span>
          </div>
        </motion.div>

        {/* Main Heading */}
        <div className="mx-auto mt-8 max-w-4xl text-center">
          <motion.h1
            className={cn(
              "from-foreground/60 via-foreground to-foreground/60 dark:from-muted-foreground/55 dark:via-foreground dark:to-muted-foreground/55 max-w-5xl bg-gradient-to-r bg-clip-text text-center text-4xl font-semibold tracking-tighter text-transparent sm:text-5xl xl:text-7xl/none",
              geist.className,
            )}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.75, delay: 0.2 }}
          >
            Intelligent
            <span className="mx-3 inline-flex items-center justify-center w-12 h-12 md:w-16 md:h-16 rounded-xl bg-gradient-to-br from-rose-500 to-rose-600 shadow-lg shadow-rose-500/25">
              <Bot className="w-6 h-6 md:w-8 md:h-8 text-white" />
            </span>
            Automation for Modern Agencies.
          </motion.h1>
        </div>

        {/* Subtitle */}
        <motion.div
          className="mx-auto mt-6 max-w-2xl text-center"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.3 }}
        >
          <p className="text-muted-foreground text-lg md:text-xl leading-relaxed">
            Deploy AI receptionists that work 24/7. Handle appointments, answer queries, and grow your business
            without increasing headcount.
          </p>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          className="mt-10 flex flex-col sm:flex-row justify-center gap-4"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.75, delay: 0.4 }}
        >
          <Link prefetch={false} href="/signup">
            <Button size="lg" className="bg-gradient-to-b from-rose-500 to-rose-700 text-white shadow-[0px_2px_0px_0px_rgba(255,255,255,0.3)_inset] hover:from-rose-600 hover:to-rose-800 transition-all duration-300 w-full sm:w-auto">
              Get Started Free
            </Button>
          </Link>
          <Link prefetch={false} href="#features">
            <Button variant="secondary" size="lg" className="w-full sm:w-auto group">
              See Demo <MoveRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </motion.div>

        {/* Tech Stack - Animated Marquee */}
        <motion.div
          className="mt-16"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.75, delay: 0.6 }}
        >
          <div className="text-center mx-auto max-w-lg mb-8">
            <h2 className="font-mono font-medium text-muted-foreground uppercase text-xs tracking-widest">
              Built with industry-leading technology
            </h2>
          </div>
          <ScrollingLogos logos={sampleLogos} />
        </motion.div>

        {/* Feature Cards */}
        <div className="mx-auto mt-16 max-w-4xl">
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.75, delay: 0.8 }}
          >
            {[
              {
                icon: Phone,
                title: "Voice AI",
                description: "Natural conversations with callers",
                color: "from-rose-500/20 to-rose-500/5",
                iconColor: "text-rose-400",
              },
              {
                icon: Calendar,
                title: "Smart Booking",
                description: "Automated appointment scheduling",
                color: "from-cyan-500/20 to-cyan-500/5",
                iconColor: "text-cyan-400",
              },
              {
                icon: MessageSquare,
                title: "24/7 Support",
                description: "Always-on customer assistance",
                color: "from-purple-500/20 to-purple-500/5",
                iconColor: "text-purple-400",
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                className={cn(
                  "group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br p-6 backdrop-blur-sm transition-all duration-300 hover:border-white/20 hover:scale-[1.02]",
                  feature.color
                )}
                whileHover={{ y: -4 }}
              >
                <div className={cn("w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4", feature.iconColor)}>
                  <feature.icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </div>
  )
}
