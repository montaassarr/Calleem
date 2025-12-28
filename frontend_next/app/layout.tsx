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
  title: {
    default: "Calleem - 24/7 AI Receptionist & Front Desk Assistant",
    template: "%s | Calleem"
  },
  description: "Automate your business calls, appointment bookings, and lead generation with Calleem AI Receptionist. The ultimate 24/7 front desk ai solution to increase leads.",
  keywords: ["ai assistant", "ai receptionist", "front desk ai", "automate booking", "appointment", "increase leads with ai assistant", "ai solution", "24/7 AI Receptionist", "Automated Answering Service"],
  authors: [{ name: "Calleem Team" }],
  creator: "Calleem",
  publisher: "Calleem",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://calleem.tech",
    siteName: "Calleem",
    title: "Calleem - AI Receptionist for Modern Businesses",
    description: "Never miss a call again. Our AI-powered receptionist handles your front desk 24/7, booking appointments and capturing leads effortlessly.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Calleem AI Receptionist",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Calleem - AI Receptionist & Front Desk Assistant",
    description: "Automate your business with Calleem AI. 24/7 phone answering, appointment booking, and lead generation.",
    images: ["/og-image.png"],
    creator: "@calleem",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
  alternates: {
    canonical: "https://calleem.tech",
  },
  manifest: "/site.webmanifest",
}

const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Calleem",
  "url": "https://calleem.tech",
  "logo": "https://calleem.tech/logo.png",
  "sameAs": [
    "https://twitter.com/calleem",
    "https://linkedin.com/company/calleem"
  ]
};

const softwareSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Calleem AI Receptionist",
  "operatingSystem": "All",
  "applicationCategory": "BusinessApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "ratingCount": "120"
  }
};


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
        <script
          type="application/ld-json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
        <script
          type="application/ld-json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(softwareSchema) }}
        />
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
