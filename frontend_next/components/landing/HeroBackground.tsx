'use client'

import React from 'react'
import { cn } from '@/lib/utils'

interface HeroBackgroundProps {
    /**
     * Whether the background should be visible.
     * Usually controlled by an IntersectionObserver on the Hero section.
     */
    isVisible: boolean
    /**
     * The animated content (Lottie, Video, Canvas, etc.).
     */
    children?: React.ReactNode
    /**
     * Optional class name for the container.
     */
    className?: string
}

export function HeroBackground({
    isVisible,
    children,
    className,
}: HeroBackgroundProps) {
    return (
        <div
            aria-hidden="true"
            className={cn(
                'fixed inset-0 z-0 h-screen w-full overflow-hidden pointer-events-none',
                'transition-opacity duration-[800ms] ease-in-out',
                isVisible ? 'opacity-100' : 'opacity-0',
                className
            )}
        >
            {/* 
        Performance Optimization:
        We keep the content mounted but hidden to avoid re-initialization costs of heavy WebGL/Canvas contexts.
        However, for very heavy animations, you might want to pause them when opacity is 0.
      */}
            <div className="absolute inset-0 w-full h-full">
                {children || (
                    // Simple blue/black gradient - high performance
                    <div className="w-full h-full bg-gradient-to-br from-blue-950 via-slate-900 to-black" />
                )}
            </div>

            {/* Optional Overlay for text readability */}
            <div className="absolute inset-0 bg-black/20" />
        </div>
    )
}
