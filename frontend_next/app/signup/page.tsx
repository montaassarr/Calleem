import { FrostedGlassAuth } from "@/components/auth/FrostedGlassAuth"

export default function SignupPage() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-[#648768]">
      <FrostedGlassAuth initialMode="signup" />
    </div>
  )
}
