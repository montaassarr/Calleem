"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";

// Dynamically import components that use Vapi hooks to prevent SSR
const CallButton = dynamic(
  () => import("@/components/vapi/CallButton").then((mod) => mod.CallButton),
  { ssr: false }
);

// Import useVapi conditionally
const VapiStatus = dynamic(
  () => import("./VapiStatus"),
  { ssr: false }
);

export default function VapiTestPage() {
  const [assistantId, setAssistantId] = useState<string>("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const params = new URLSearchParams(window.location.search);
    const a = params.get("assistantId");
    if (a) setAssistantId(a);
  }, []);

  if (!mounted) {
    return (
      <div className="max-w-2xl mx-auto py-8">
        <h1 className="text-2xl font-semibold">Vapi Test Call</h1>
        <p className="text-sm text-muted-foreground mt-2">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-8">
      <h1 className="text-2xl font-semibold">Vapi Test Call</h1>
      <p className="text-sm text-muted-foreground mt-2">
        Provide an `assistantId` in the URL query or enter below.
      </p>

      <div className="mt-6 flex items-center gap-2">
        <input
          className="border rounded px-3 py-2 w-full"
          placeholder="Assistant ID"
          value={assistantId}
          onChange={(e) => setAssistantId(e.target.value)}
        />
        <CallButton assistantId={assistantId} />
      </div>

      <VapiStatus />
    </div>
  );
}
