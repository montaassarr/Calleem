(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/frontend_next/lib/load-script.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "loadScript",
    ()=>loadScript
]);
function loadScript(src) {
    return new Promise((resolve, reject)=>{
        const script = document.createElement("script");
        script.src = src;
        script.onload = ()=>resolve();
        script.onerror = ()=>reject(new Error(`Failed to load script: ${src}`));
        document.head.appendChild(script);
    });
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=frontend_next_lib_load-script_ts_fafcabd8._.js.map