"use client"

export function BackgroundContent() {
    return (
        <div className="absolute inset-0 w-full h-full bg-[#648768]">
            {/* Green background with subtle overlays */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(142, 194, 149, 0.15),transparent_50%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(30,80,50,0.2),transparent_50%)]" />
        </div>
    )
}
