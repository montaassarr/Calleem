"use client";

import React from "react";
import dynamic from "next/dynamic";

// Dynamically import the entire component to prevent SSR
const VapiTestContent = dynamic(
  () => import("@/app/admin/vapi-test/VapiTestContent"),
  { ssr: false, loading: () => (
    <div className="max-w-2xl mx-auto py-8">
      <h1 className="text-2xl font-semibold">Vapi Test Call</h1>
      <p className="text-sm text-muted-foreground mt-2">Loading...</p>
    </div>
  )}
);

export default function VapiTestPage() {
  return <VapiTestContent />;
}
