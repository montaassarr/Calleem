"use client"

export function BackgroundContent() {
    return (
        <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-blue-950 via-slate-900 to-black">
            {/* Simple blue and black gradient - high performance */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.15),transparent_50%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(30,58,138,0.2),transparent_50%)]" />
        </div>
    )
}
