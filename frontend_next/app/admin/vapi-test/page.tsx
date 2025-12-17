"use client";

import React, { useEffect, useMemo, useState } from "react";
import { CallButton } from "@/components/vapi/CallButton";
import { useVapi } from "@/components/vapi/VapiProvider";

// Prevent SSR to avoid VapiProvider issues during build
export const dynamic = 'force-dynamic';

export default function VapiTestPage() {
  const { status } = useVapi();
  const [assistantId, setAssistantId] = useState<string>("");

  // Read assistantId from query for quick testing
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const a = params.get("assistantId");
    if (a) setAssistantId(a);
  }, []);

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

      <div className="mt-8 p-4 rounded border bg-secondary/20">
        <div className="font-medium">Connection Status</div>
        <div className="mt-2 text-sm">{status}</div>
      </div>
    </div>
  );
}
