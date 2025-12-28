
import { FrostedGlassAuth } from "@/components/auth/FrostedGlassAuth"

export default function AdminLoginPage() {
    return (
        <div className="min-h-screen w-full flex items-center justify-center p-4 bg-slate-950">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-white mb-2">Admin Panel</h1>
                    <p className="text-slate-400">Restricted access area</p>
                </div>
                <FrostedGlassAuth initialMode="login" />
            </div>
        </div>
    )
}
