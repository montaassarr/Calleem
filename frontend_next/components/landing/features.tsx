"use client"

import type React from "react"
import { motion, useInView } from "framer-motion"
import { useRef, useState } from "react"
import { geist } from "@/lib/fonts"
import { cn } from "@/lib/utils"
import { Send, Mic, MicOff } from "lucide-react"
import { GlassCard } from "@/components/ui/glass-card"

export default function Features() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.3 })
  const [inputValue, setInputValue] = useState("")
  const [isRecording, setIsRecording] = useState(false)
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([
    { role: "assistant", content: "Hi! I'm your AI receptionist. How can I help you today?" }
  ])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    setChatMessages(prev => [...prev, { role: "user", content: inputValue }])
    setInputValue("")

    // Simulate AI response
    setTimeout(() => {
      setChatMessages(prev => [...prev, {
        role: "assistant",
        content: "I've received your message. This is a demo interface showcasing Chat AI capabilities."
      }])
    }, 1000)
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // Simulate voice recording
    if (!isRecording) {
      setTimeout(() => {
        setChatMessages(prev => [...prev, {
          role: "assistant",
          content: "Voice AI demo: I'm listening... (This is a demo interface)"
        }])
        setIsRecording(false)
      }, 2000)
    }
  }

  return (
    <section id="features" className="text-foreground relative overflow-hidden py-12 sm:py-24 md:py-32">
      <div className="bg-primary absolute -top-10 left-1/2 h-16 w-44 -translate-x-1/2 rounded-full opacity-40 blur-3xl select-none"></div>
      <div className="via-primary/50 absolute top-0 left-1/2 h-px w-3/5 -translate-x-1/2 bg-gradient-to-r from-transparent to-transparent transition-all ease-in-out"></div>

      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 50 }}
        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
        transition={{ duration: 0.5, delay: 0 }}
        className="container mx-auto flex flex-col items-center gap-6 sm:gap-12"
      >
        <h2
          className={cn(
            "via-foreground mb-8 bg-gradient-to-b from-zinc-800 to-zinc-700 bg-clip-text text-center text-4xl font-semibold tracking-tighter text-transparent md:text-[54px] md:leading-[60px]",
            geist.className,
          )}
        >
          AI Demo
        </h2>

        {/* Single Interactive Demo Card */}
        <motion.div
          className="group border-white/10 bg-slate-950/70 backdrop-blur-xl text-card-foreground relative w-full max-w-4xl overflow-hidden rounded-3xl border shadow-2xl transition-all ease-in-out"
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          whileHover={{
            scale: 1.01,
            borderColor: "rgba(8, 145, 178, 0.6)",
            boxShadow: "0 0 30px rgba(8, 145, 178, 0.2)",
          }}
        >
          {/* Subtle gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-transparent rounded-3xl pointer-events-none" />

          <div className="relative p-8">
            <div className="flex flex-col gap-6">
              {/* Header */}
              <div className="flex flex-col gap-2">
                <h3 className="text-3xl leading-none font-semibold tracking-tight">Chat AI & Voice AI Demo</h3>
                <p className="text-muted-foreground text-sm">
                  Experience our AI receptionist's natural conversation capabilities through chat or voice
                </p>
              </div>

              {/* Chat Messages */}
              <div className="flex flex-col gap-3 min-h-[300px] max-h-[400px] overflow-y-auto p-4 rounded-2xl border border-white/10 bg-black/20 dark:bg-white/5 backdrop-blur-sm">
                {chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      "flex",
                      msg.role === "user" ? "justify-end" : "justify-start"
                    )}
                  >
                    <div
                      className={cn(
                        "max-w-[80%] rounded-2xl px-4 py-2",
                        msg.role === "user"
                          ? "bg-cyan-600/80 text-white"
                          : "bg-white/10 text-white/90 border border-white/10"
                      )}
                    >
                      {msg.content}
                    </div>
                  </div>
                ))}
              </div>

              {/* Input Area */}
              <div className="flex items-center gap-3">
                <div className="flex-1 relative rounded-2xl border border-white/10 bg-black/20 dark:bg-white/5 backdrop-blur-sm">
                  <textarea
                    className="w-full min-h-[60px] bg-transparent border-none text-white placeholder:text-white/50 resize-none focus:outline-none text-base leading-relaxed p-4"
                    placeholder="Type your message or use voice..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                  />
                </div>

                {/* Voice Button */}
                <button
                  onClick={toggleRecording}
                  className={cn(
                    "p-4 rounded-full transition-all duration-300 shadow-lg",
                    isRecording
                      ? "bg-red-600 hover:bg-red-500 animate-pulse"
                      : "bg-white/10 hover:bg-white/20"
                  )}
                >
                  {isRecording ? (
                    <MicOff className="w-6 h-6 text-white" />
                  ) : (
                    <Mic className="w-6 h-6 text-white" />
                  )}
                </button>

                {/* Send Button */}
                <button
                  onClick={handleSendMessage}
                  className="p-4 rounded-full bg-cyan-600 hover:bg-cyan-500 transition-colors text-white shadow-[0_0_15px_rgba(8,145,178,0.3)]"
                >
                  <Send className="w-6 h-6" />
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}
