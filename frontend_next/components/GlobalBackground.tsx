'use client'

import { usePathname } from 'next/navigation'
import { HeroBackground } from '@/components/HeroBackground'
import { BackgroundContent } from '@/components/BackgroundContent'

export function GlobalBackground() {
    const pathname = usePathname()

    // Don't render on dashboard pages
    if (pathname?.startsWith('/dashboard')) {
        return null
    }

    // Don't render on home page (Hero component handles it with scroll logic)
    if (pathname === '/') {
        return null
    }

    // Render always visible for other public pages (Login, Signup, etc.)
    return (
        <HeroBackground isVisible={true}>
            <BackgroundContent />
        </HeroBackground>
    )
}
