
import { Lock } from "lucide-react"
import { FrostedGlassAuth } from "@/components/auth/FrostedGlassAuth"

export default function AdminLoginPage() {
    return (
        <div className="min-h-screen w-full flex items-center justify-center p-4 bg-background">
            <div className="w-full max-w-md">
                <div className="mb-8 flex flex-col items-center text-center">
                    <svg viewBox="0 0 41 24" className="mb-5 h-8 w-14 text-[#8cff2e]" fill="currentColor" aria-hidden>
                        <g transform="translate(0 0.5)">
                            <path d="M 21.821 0.929 C 22.354 0.38 23.092 0.068 23.865 0.065 L 33.762 0.065 C 40.198 0.065 43.42 8.011 38.869 12.659 L 28.958 22.783 C 28.503 23.247 27.725 22.918 27.725 22.26 L 27.725 13.345 L 28.87 12.174 C 29.78 11.245 29.136 9.656 27.848 9.656 L 13.276 9.656 L 21.821 0.929 Z" />
                            <path d="M 19.179 22.071 C 18.646 22.62 17.908 22.932 17.135 22.935 L 7.238 22.935 C 0.802 22.935 -2.42 14.988 2.131 10.341 L 12.042 0.217 C 12.497 -0.247 13.276 0.082 13.276 0.739 L 13.276 9.655 L 12.13 10.825 C 11.22 11.755 11.864 13.344 13.152 13.344 L 27.724 13.344 L 19.178 22.071 Z" />
                        </g>
                    </svg>
                    <h1 className="font-host text-2xl font-bold tracking-tight text-white">Calleem super admin</h1>
                    <p className="mt-2 flex items-center gap-1.5 text-sm text-muted-foreground">
                        <Lock className="size-3.5" /> Private console · this PC only
                    </p>
                </div>
                <FrostedGlassAuth initialMode="login" />
            </div>
        </div>
    )
}
