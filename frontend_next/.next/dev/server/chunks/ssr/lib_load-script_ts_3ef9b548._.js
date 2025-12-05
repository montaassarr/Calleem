module.exports = [
"[project]/lib/load-script.ts [app-ssr] (ecmascript, async loader)", ((__turbopack_context__) => {

__turbopack_context__.v((parentImport) => {
    return Promise.all([
  "server/chunks/ssr/lib_load-script_ts_2a9168b3._.js"
].map((chunk) => __turbopack_context__.l(chunk))).then(() => {
        return parentImport("[project]/lib/load-script.ts [app-ssr] (ecmascript)");
    });
});
}),
];