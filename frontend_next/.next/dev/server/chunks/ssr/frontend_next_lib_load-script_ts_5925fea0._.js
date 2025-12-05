module.exports = [
"[project]/frontend_next/lib/load-script.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
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
}),
];

//# sourceMappingURL=frontend_next_lib_load-script_ts_5925fea0._.js.map