"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AISettingsPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/dashboard/voice-agent/control-center");
  }, [router]);

  return (
    <div className="flex items-center justify-center p-12">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#0a4c2f]" />
    </div>
  );
}
