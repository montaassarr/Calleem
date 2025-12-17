"use client";

import { useVapi } from "@/components/vapi/VapiProvider";

export default function VapiStatus() {
  const { status } = useVapi();

  return (
    <div className="mt-8 p-4 rounded border bg-secondary/20">
      <div className="font-medium">Connection Status</div>
      <div className="mt-2 text-sm">{status}</div>
    </div>
  );
}
