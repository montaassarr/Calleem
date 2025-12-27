import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import "./globals.css"

import { Archivo as V0_Font_Archivo, Geist_Mono as V0_Font_Geist_Mono, Source_Serif_4 as V0_Font_Source_Serif_4 } from 'next/font/google'

// Initialize fonts
const _archivo = V0_Font_Archivo({ subsets: ['latin'], weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"] })
const _geistMono = V0_Font_Geist_Mono({ subsets: ['latin'], weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"] })
const _sourceSerif_4 = V0_Font_Source_Serif_4({ subsets: ['latin'], weight: ["200", "300", "400", "500", "600", "700", "800", "900"] })

export const metadata: Metadata = {
  title: "AIM² - AI Receptionist Agency",
  description: "Automate your business with AIM² AI Receptionist",
  generator: "v0.app",
}


import Providers from "@/components/providers"

// ... imports ...

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <style>{`
html {
  font-family: ${GeistSans.style.fontFamily};
  --font-sans: ${GeistSans.variable};
  --font-sans: ${GeistMono.variable};
}
        `}</style>
      </head>
      <body className="dark" suppressHydrationWarning>
        <Providers>

          {children}
        </Providers>
      </body>
    </html>
  )
}
