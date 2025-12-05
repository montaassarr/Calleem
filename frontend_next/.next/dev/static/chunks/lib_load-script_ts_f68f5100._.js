(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/lib/load-script.ts [app-client] (ecmascript, async loader)", ((__turbopack_context__) => {

__turbopack_context__.v((parentImport) => {
    return Promise.all([
  "static/chunks/lib_load-script_ts_4bc128bd._.js",
  "static/chunks/lib_load-script_ts_64a138ca._.js"
].map((chunk) => __turbopack_context__.l(chunk))).then(() => {
        return parentImport("[project]/lib/load-script.ts [app-client] (ecmascript)");
    });
});
}),
]);