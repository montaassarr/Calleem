(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/components/voice-agent/voice-app.tsx [app-client] (ecmascript, next/dynamic entry, async loader)", ((__turbopack_context__) => {

__turbopack_context__.v((parentImport) => {
    return Promise.all([
  "static/chunks/node_modules_livekit-client_dist_livekit-client_esm_mjs_00ea67ad._.js",
  "static/chunks/node_modules_@livekit_components-react_dist_810fcbe5._.js",
  "static/chunks/components_voice-agent_voice-app_tsx_8781c8a6._.js",
  {
    "path": "static/chunks/node_modules_@livekit_components-styles_dist_general_index_b89432ec.css",
    "included": [
      "[project]/node_modules/@livekit/components-styles/dist/general/index.css [app-client] (css)"
    ]
  },
  "static/chunks/components_voice-agent_voice-app_tsx_b5fd97bc._.js"
].map((chunk) => __turbopack_context__.l(chunk))).then(() => {
        return parentImport("[project]/components/voice-agent/voice-app.tsx [app-client] (ecmascript, next/dynamic entry)");
    });
});
}),
]);