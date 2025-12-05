module.exports = [
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/action-async-storage.external.js [external] (next/dist/server/app-render/action-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/action-async-storage.external.js", () => require("next/dist/server/app-render/action-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[project]/lib/utils.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "cn",
    ()=>cn
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/clsx/dist/clsx.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/tailwind-merge/dist/bundle-mjs.mjs [app-ssr] (ecmascript)");
;
;
function cn(...inputs) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["twMerge"])((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clsx"])(inputs));
}
}),
"[project]/components/HeroBackground.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "HeroBackground",
    ()=>HeroBackground
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/utils.ts [app-ssr] (ecmascript)");
'use client';
;
;
function HeroBackground({ isVisible, children, className }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "aria-hidden": "true",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])('fixed inset-0 z-0 h-screen w-full overflow-hidden pointer-events-none', 'transition-opacity duration-[800ms] ease-in-out', isVisible ? 'opacity-100' : 'opacity-0', className),
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "absolute inset-0 w-full h-full",
                children: children || // Simple blue/black gradient - high performance
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "w-full h-full bg-gradient-to-br from-blue-950 via-slate-900 to-black"
                }, void 0, false, {
                    fileName: "[project]/components/HeroBackground.tsx",
                    lineNumber: 45,
                    columnNumber: 21
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/HeroBackground.tsx",
                lineNumber: 42,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "absolute inset-0 bg-black/20"
            }, void 0, false, {
                fileName: "[project]/components/HeroBackground.tsx",
                lineNumber: 50,
                columnNumber: 13
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/HeroBackground.tsx",
        lineNumber: 28,
        columnNumber: 9
    }, this);
}
}),
"[project]/components/BackgroundContent.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "BackgroundContent",
    ()=>BackgroundContent
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
"use client";
;
function BackgroundContent() {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "absolute inset-0 w-full h-full bg-gradient-to-br from-blue-950 via-slate-900 to-black",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.15),transparent_50%)]"
            }, void 0, false, {
                fileName: "[project]/components/BackgroundContent.tsx",
                lineNumber: 7,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(30,58,138,0.2),transparent_50%)]"
            }, void 0, false, {
                fileName: "[project]/components/BackgroundContent.tsx",
                lineNumber: 8,
                columnNumber: 13
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/BackgroundContent.tsx",
        lineNumber: 5,
        columnNumber: 9
    }, this);
}
}),
"[project]/components/GlobalBackground.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "GlobalBackground",
    ()=>GlobalBackground
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$HeroBackground$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/HeroBackground.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$BackgroundContent$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/BackgroundContent.tsx [app-ssr] (ecmascript)");
'use client';
;
;
;
;
function GlobalBackground() {
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    // Don't render on dashboard pages
    if (pathname?.startsWith('/dashboard')) {
        return null;
    }
    // Don't render on home page (Hero component handles it with scroll logic)
    if (pathname === '/') {
        return null;
    }
    // Render always visible for other public pages (Login, Signup, etc.)
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$HeroBackground$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["HeroBackground"], {
        isVisible: true,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$BackgroundContent$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["BackgroundContent"], {}, void 0, false, {
            fileName: "[project]/components/GlobalBackground.tsx",
            lineNumber: 23,
            columnNumber: 13
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/GlobalBackground.tsx",
        lineNumber: 22,
        columnNumber: 9
    }, this);
}
}),
"[externals]/util [external] (util, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("util", () => require("util"));

module.exports = mod;
}),
"[externals]/stream [external] (stream, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("stream", () => require("stream"));

module.exports = mod;
}),
"[externals]/path [external] (path, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("path", () => require("path"));

module.exports = mod;
}),
"[externals]/http [external] (http, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("http", () => require("http"));

module.exports = mod;
}),
"[externals]/https [external] (https, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("https", () => require("https"));

module.exports = mod;
}),
"[externals]/url [external] (url, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("url", () => require("url"));

module.exports = mod;
}),
"[externals]/fs [external] (fs, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("fs", () => require("fs"));

module.exports = mod;
}),
"[externals]/crypto [external] (crypto, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("crypto", () => require("crypto"));

module.exports = mod;
}),
"[externals]/http2 [external] (http2, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("http2", () => require("http2"));

module.exports = mod;
}),
"[externals]/assert [external] (assert, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("assert", () => require("assert"));

module.exports = mod;
}),
"[externals]/tty [external] (tty, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("tty", () => require("tty"));

module.exports = mod;
}),
"[externals]/os [external] (os, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("os", () => require("os"));

module.exports = mod;
}),
"[externals]/zlib [external] (zlib, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("zlib", () => require("zlib"));

module.exports = mod;
}),
"[externals]/events [external] (events, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("events", () => require("events"));

module.exports = mod;
}),
"[project]/lib/api.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "apiClient",
    ()=>apiClient,
    "default",
    ()=>__TURBOPACK__default__export__
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/axios/lib/axios.js [app-ssr] (ecmascript)");
;
const BASE_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api/v1`;
class ApiClient {
    client;
    constructor(){
        this.client = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        // Request interceptor to add auth token and tenant ID
        this.client.interceptors.request.use((config)=>{
            const token = localStorage.getItem('access_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            // Add X-Tenant-ID header if available
            const tenantId = localStorage.getItem('tenant_id');
            if (tenantId) {
                config.headers['X-Tenant-ID'] = tenantId;
            }
            // Fallback: try to get tenant_id from user object
            if (!tenantId) {
                const userStr = localStorage.getItem('user');
                if (userStr) {
                    try {
                        const user = JSON.parse(userStr);
                        if (user.tenant_id) {
                            config.headers['X-Tenant-ID'] = user.tenant_id;
                            // Cache it for next time
                            localStorage.setItem('tenant_id', user.tenant_id);
                        }
                    } catch (e) {
                        console.error('Error parsing user data:', e);
                    }
                }
            }
            return config;
        }, (error)=>Promise.reject(error));
        // Response interceptor for error handling
        this.client.interceptors.response.use((response)=>response, (error)=>{
            // Only redirect to login on 401 if it's not a config fetch
            // Config fetch failures should be handled gracefully by the component
            const isConfigEndpoint = error.config?.url?.includes('/admin/config');
            if (error.response?.status === 401 && !isConfigEndpoint) {
                // Redirect to login on unauthorized (but not for config fetches)
                if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
                ;
            }
            return Promise.reject(error);
        });
    }
    async get(url, config) {
        const response = await this.client.get(url, config);
        return response.data;
    }
    async post(url, data, config) {
        const response = await this.client.post(url, data, config);
        return response.data;
    }
    async put(url, data, config) {
        const response = await this.client.put(url, data, config);
        return response.data;
    }
    async delete(url, config) {
        const response = await this.client.delete(url, config);
        return response.data;
    }
    async patch(url, data, config) {
        const response = await this.client.patch(url, data, config);
        return response.data;
    }
}
const apiClient = new ApiClient();
const __TURBOPACK__default__export__ = apiClient;
}),
"[project]/lib/api/auth.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "authApi",
    ()=>authApi
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-ssr] (ecmascript)");
;
const authApi = {
    /**
     * Login user and get JWT token
     * Sends email as username since backend supports both
     */ login: async (credentials)=>{
        const formData = new URLSearchParams();
        // Send email as username - backend now supports email lookup
        const username = credentials.username || credentials.email || '';
        formData.append('username', username);
        formData.append('password', credentials.password);
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post('/users/token', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        return response; // ApiClient already returns .data
    },
    /**
     * Register a new user
     */ register: async (userData)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post('/users/register', userData);
        return response; // ApiClient already returns .data
    },
    /**
     * Get current authenticated user
     */ getCurrentUser: async ()=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get('/users/me');
        return response; // ApiClient already returns .data
    },
    /**
     * Logout user (client-side only)
     */ logout: ()=>{
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
    }
};
}),
"[project]/lib/errorLogging.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "authenticatedFetch",
    ()=>authenticatedFetch,
    "fetchWithLogging",
    ()=>fetchWithLogging,
    "logClientError",
    ()=>logClientError,
    "logUserAction",
    ()=>logUserAction,
    "parseJsonResponse",
    ()=>parseJsonResponse,
    "trackPerformance",
    ()=>trackPerformance
]);
const BASE_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || "http://localhost:8000";
const API_BASE = `${BASE_URL}/api/v1`;
const LEVELS = [
    "debug",
    "info",
    "warning",
    "error",
    "critical"
];
async function postDiagnostics(path, payload) {
    try {
        const response = await fetch(`${API_BASE}/monitoring/${path}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            console.warn(`Diagnostics endpoint ${path} responded with`, response.status);
        }
    } catch (error) {
        console.warn("Failed to send diagnostics", error);
    }
}
async function logClientError(message, options) {
    await postDiagnostics("frontend-error", {
        message,
        level: options?.level || "error",
        stack: options?.stack,
        component: options?.component,
        url: options?.url || (("TURBOPACK compile-time falsy", 0) ? "TURBOPACK unreachable" : undefined),
        metadata: options?.metadata || {},
        user_id: options?.userId || undefined,
        tenant_id: options?.tenantId || undefined
    });
}
async function logUserAction(action, data, options) {
    await postDiagnostics("frontend-action", {
        action,
        data: data || {},
        user_id: options?.userId || undefined,
        tenant_id: options?.tenantId || undefined,
        success: options?.success ?? true
    });
}
async function trackPerformance(metric, duration, options) {
    await postDiagnostics("frontend-performance", {
        metric,
        duration_ms: duration,
        user_id: options?.userId || undefined,
        tenant_id: options?.tenantId || undefined,
        metadata: options?.metadata || {}
    });
}
async function fetchWithLogging(url, options) {
    const startTime = typeof performance !== "undefined" ? performance.now() : Date.now();
    try {
        const response = await fetch(url, options);
        const duration = (typeof performance !== "undefined" ? performance.now() : Date.now()) - startTime;
        if (duration > 2000) {
            trackPerformance("slow_api_call", duration, {
                metadata: {
                    url,
                    method: options?.method || "GET"
                }
            });
        }
        if (!response.ok) {
            const preview = await response.clone().text();
            await logClientError(`API Error: ${response.status} ${response.statusText}`, {
                level: "error",
                metadata: {
                    url,
                    method: options?.method || "GET",
                    status: response.status,
                    responseBody: preview.substring(0, 1000)
                }
            });
        }
        return response;
    } catch (error) {
        const duration = (typeof performance !== "undefined" ? performance.now() : Date.now()) - startTime;
        await logClientError(error instanceof Error ? error.message : "Unknown fetch error", {
            level: "critical",
            stack: error instanceof Error ? error.stack : undefined,
            metadata: {
                url,
                method: options?.method || "GET",
                duration
            }
        });
        throw error;
    }
}
async function authenticatedFetch(url, options) {
    if ("TURBOPACK compile-time truthy", 1) {
        throw new Error("authenticatedFetch can only run in the browser");
    }
    const token = window.localStorage.getItem("access_token");
    if (!token) {
        await logClientError("Missing authentication token", {
            level: "warning",
            metadata: {
                url
            }
        });
        throw new Error("Authentication required");
    }
    const headers = new Headers(options?.headers);
    headers.set("Authorization", `Bearer ${token}`);
    headers.set("Content-Type", "application/json");
    return fetchWithLogging(url, {
        ...options,
        headers
    });
}
async function parseJsonResponse(response) {
    try {
        return await response.json();
    } catch (error) {
        await logClientError("Failed to parse JSON response", {
            level: "error",
            metadata: {
                url: response.url,
                status: response.status,
                statusText: response.statusText
            },
            stack: error instanceof Error ? error.stack : undefined
        });
        throw new Error("Failed to parse JSON response");
    }
}
}),
"[project]/contexts/AuthContext.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AuthProvider",
    ()=>AuthProvider,
    "useAuth",
    ()=>useAuth
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/auth.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/errorLogging.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
const AuthContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createContext"])(undefined);
function AuthProvider({ children }) {
    const [user, setUser] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    // Check for existing session on mount
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const initAuth = async ()=>{
            if ("TURBOPACK compile-time truthy", 1) return;
            //TURBOPACK unreachable
            ;
            const token = undefined;
        };
        initAuth();
    }, []);
    const login = async (credentials)=>{
        setIsLoading(true);
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logUserAction"])('login_attempt', {
            email: credentials.email
        });
        try {
            const token = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["authApi"].login(credentials);
            localStorage.setItem('access_token', token.access_token);
            // Fetch user profile immediately
            const userData = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["authApi"].getCurrentUser();
            setUser(userData);
            // Store user data in localStorage for components that need it
            localStorage.setItem('user', JSON.stringify(userData));
            if (userData.tenant_id) {
                localStorage.setItem('tenant_id', userData.tenant_id);
            }
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logUserAction"])('login_success', {
                user_id: userData.id,
                tenant_id: userData.tenant_id,
                role: userData.role
            }, {
                userId: userData.id,
                tenantId: userData.tenant_id
            });
            // Redirect based on role
            if (userData.role === 'super_admin') {
                window.location.href = '/admin/dashboard';
            } else {
                window.location.href = '/dashboard';
            }
        } catch (error) {
            console.error('Login failed:', error);
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logClientError"])('Login failed', {
                metadata: {
                    email: credentials.email
                },
                stack: error instanceof Error ? error.stack : undefined
            });
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logUserAction"])('login_failed', {
                email: credentials.email
            }, {
                userId: user?.id,
                tenantId: user?.tenant_id,
                success: false
            });
            throw error;
        } finally{
            setIsLoading(false);
        }
    };
    const register = async (data)=>{
        setIsLoading(true);
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logUserAction"])('registration_attempt', {
            email: data.email,
            username: data.username,
            business_name: data.business_name
        });
        try {
            // Backend returns token on registration
            const token = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["authApi"].register(data);
            localStorage.setItem('access_token', token.access_token);
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logUserAction"])('registration_token_received');
            // Fetch user profile immediately after registration
            const userData = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["authApi"].getCurrentUser();
            setUser(userData);
            // Store user data in localStorage for components that need it
            localStorage.setItem('user', JSON.stringify(userData));
            if (userData.tenant_id) {
                localStorage.setItem('tenant_id', userData.tenant_id);
            }
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logUserAction"])('registration_success', {
                user_id: userData.id,
                tenant_id: userData.tenant_id,
                business_name: data.business_name
            }, {
                userId: userData.id,
                tenantId: userData.tenant_id
            });
            // Redirect to dashboard after successful registration
            window.location.href = '/dashboard';
        } catch (error) {
            console.error('Registration failed:', error);
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logClientError"])('Registration failed', {
                metadata: {
                    email: data.email,
                    username: data.username,
                    business_name: data.business_name
                },
                stack: error instanceof Error ? error.stack : undefined
            });
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logUserAction"])('registration_failed', {
                email: data.email,
                error: error instanceof Error ? error.message : 'Unknown error'
            }, {
                userId: null,
                tenantId: null,
                success: false
            });
            throw error;
        } finally{
            setIsLoading(false);
        }
    };
    const logout = ()=>{
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$errorLogging$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["logUserAction"])('logout', {
            user_id: user?.id
        }, {
            userId: user?.id ?? undefined,
            tenantId: user?.tenant_id ?? undefined
        });
        __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$auth$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["authApi"].logout();
        localStorage.removeItem('tenant_id');
        localStorage.removeItem('user');
        setUser(null);
        router.push('/login');
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(AuthContext.Provider, {
        value: {
            user,
            isLoading,
            login,
            register,
            logout,
            isAuthenticated: !!user
        },
        children: children
    }, void 0, false, {
        fileName: "[project]/contexts/AuthContext.tsx",
        lineNumber: 186,
        columnNumber: 9
    }, this);
}
function useAuth() {
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useContext"])(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
}),
"[project]/lib/api/business-config.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "businessConfigApi",
    ()=>businessConfigApi
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-ssr] (ecmascript)");
;
const businessConfigApi = {
    /**
     * Get current business configuration
     */ getConfig: async (businessId = 'default')=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get('/admin/config');
        return response; // ApiClient already returns .data
    },
    /**
     * Update business configuration
     */ updateConfig: async (data, businessId = 'default')=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put('/admin/config', data);
        return response; // ApiClient already returns .data
    },
    updateFeatureFlags: async (features, businessId = 'default')=>{
        // First get current config to merge
        const current = await businessConfigApi.getConfig();
        const updatedFeatures = {
            ...current.features_enabled,
            ...features
        };
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put('/admin/config', {
            automations: updatedFeatures
        });
        return response; // ApiClient already returns .data
    },
    updateAutomations: async (automations, businessId = 'default')=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put('/admin/config', {
            automations
        });
        return response; // ApiClient already returns .data
    },
    /**
     * Reload configuration (invalidate cache)
     */ reloadConfig: async (businessId = 'default')=>{
        return {
            message: "Config reloaded"
        };
    },
    /**
     * Get AI prompt configuration
     */ getAIPrompt: async (businessId = 'default')=>{
        const config = await businessConfigApi.getConfig();
        return {
            system_prompt: config.ai_config?.system_prompt || ""
        };
    },
    /**
     * Update AI prompt
     */ updateAIPrompt: async (systemPrompt, businessId = 'default')=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put('/admin/config', {
            system_prompt: systemPrompt
        });
        return response; // ApiClient already returns .data
    },
    /**
     * Update WhatsApp configuration
     */ updateWhatsAppConfig: async (config, businessId = 'default')=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put('/admin/config', {
            whatsapp_config: config
        });
        return response; // ApiClient already returns .data
    },
    /**
     * Get services list
     */ getServices: async (businessId = 'default')=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get('/services/');
        return response; // ApiClient already returns .data
    }
};
}),
"[project]/hooks/use-toast.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "reducer",
    ()=>reducer,
    "toast",
    ()=>toast,
    "useToast",
    ()=>useToast
]);
// Inspired by react-hot-toast library
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
'use client';
;
const TOAST_LIMIT = 1;
const TOAST_REMOVE_DELAY = 1000000;
const actionTypes = {
    ADD_TOAST: 'ADD_TOAST',
    UPDATE_TOAST: 'UPDATE_TOAST',
    DISMISS_TOAST: 'DISMISS_TOAST',
    REMOVE_TOAST: 'REMOVE_TOAST'
};
let count = 0;
function genId() {
    count = (count + 1) % Number.MAX_SAFE_INTEGER;
    return count.toString();
}
const toastTimeouts = new Map();
const addToRemoveQueue = (toastId)=>{
    if (toastTimeouts.has(toastId)) {
        return;
    }
    const timeout = setTimeout(()=>{
        toastTimeouts.delete(toastId);
        dispatch({
            type: 'REMOVE_TOAST',
            toastId: toastId
        });
    }, TOAST_REMOVE_DELAY);
    toastTimeouts.set(toastId, timeout);
};
const reducer = (state, action)=>{
    switch(action.type){
        case 'ADD_TOAST':
            return {
                ...state,
                toasts: [
                    action.toast,
                    ...state.toasts
                ].slice(0, TOAST_LIMIT)
            };
        case 'UPDATE_TOAST':
            return {
                ...state,
                toasts: state.toasts.map((t)=>t.id === action.toast.id ? {
                        ...t,
                        ...action.toast
                    } : t)
            };
        case 'DISMISS_TOAST':
            {
                const { toastId } = action;
                // ! Side effects ! - This could be extracted into a dismissToast() action,
                // but I'll keep it here for simplicity
                if (toastId) {
                    addToRemoveQueue(toastId);
                } else {
                    state.toasts.forEach((toast)=>{
                        addToRemoveQueue(toast.id);
                    });
                }
                return {
                    ...state,
                    toasts: state.toasts.map((t)=>t.id === toastId || toastId === undefined ? {
                            ...t,
                            open: false
                        } : t)
                };
            }
        case 'REMOVE_TOAST':
            if (action.toastId === undefined) {
                return {
                    ...state,
                    toasts: []
                };
            }
            return {
                ...state,
                toasts: state.toasts.filter((t)=>t.id !== action.toastId)
            };
    }
};
const listeners = [];
let memoryState = {
    toasts: []
};
function dispatch(action) {
    memoryState = reducer(memoryState, action);
    listeners.forEach((listener)=>{
        listener(memoryState);
    });
}
function toast({ ...props }) {
    const id = genId();
    const update = (props)=>dispatch({
            type: 'UPDATE_TOAST',
            toast: {
                ...props,
                id
            }
        });
    const dismiss = ()=>dispatch({
            type: 'DISMISS_TOAST',
            toastId: id
        });
    dispatch({
        type: 'ADD_TOAST',
        toast: {
            ...props,
            id,
            open: true,
            onOpenChange: (open)=>{
                if (!open) dismiss();
            }
        }
    });
    return {
        id: id,
        dismiss,
        update
    };
}
function useToast() {
    const [state, setState] = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"](memoryState);
    __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"](()=>{
        listeners.push(setState);
        return ()=>{
            const index = listeners.indexOf(setState);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        };
    }, [
        state
    ]);
    return {
        ...state,
        toast,
        dismiss: (toastId)=>dispatch({
                type: 'DISMISS_TOAST',
                toastId
            })
    };
}
;
}),
"[project]/hooks/use-config.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useAIPrompt",
    ()=>useAIPrompt,
    "useConfig",
    ()=>useConfig,
    "useServices",
    ()=>useServices
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/useQuery.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useMutation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/useMutation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/QueryClientProvider.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$business$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/business-config.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$use$2d$toast$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/hooks/use-toast.ts [app-ssr] (ecmascript)");
;
;
;
const QUERY_KEY = 'businessConfig';
function useConfig(businessId = 'default', enabled = true) {
    const queryClient = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useQueryClient"])();
    const { toast } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$use$2d$toast$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useToast"])();
    // Get configuration
    const { data: config, isLoading, error, refetch } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            QUERY_KEY,
            businessId
        ],
        queryFn: ()=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$business$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["businessConfigApi"].getConfig(businessId),
        enabled: enabled,
        staleTime: 5 * 60 * 1000,
        retry: (failureCount, error)=>{
            // Don't retry on 401 (unauthorized) - user needs to login
            if (error?.response?.status === 401) {
                return false;
            }
            // Retry other errors up to 2 times
            return failureCount < 2;
        },
        // Don't throw errors, let components handle them
        throwOnError: false
    });
    // Update configuration
    const updateConfig = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useMutation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useMutation"])({
        mutationFn: (data)=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$business$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["businessConfigApi"].updateConfig(data, businessId),
        onSuccess: (data)=>{
            queryClient.setQueryData([
                QUERY_KEY,
                businessId
            ], data);
            toast({
                title: 'Configuration Updated',
                description: 'Business configuration has been saved successfully.'
            });
        },
        onError: (error)=>{
            toast({
                title: 'Update Failed',
                description: error.response?.data?.detail || 'Failed to update configuration',
                variant: 'destructive'
            });
        }
    });
    // Reload configuration (invalidate cache)
    const reloadConfig = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useMutation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useMutation"])({
        mutationFn: ()=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$business$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["businessConfigApi"].reloadConfig(businessId),
        onSuccess: ()=>{
            queryClient.invalidateQueries({
                queryKey: [
                    QUERY_KEY,
                    businessId
                ]
            });
            toast({
                title: 'Configuration Reloaded',
                description: 'Latest configuration loaded from database.'
            });
        }
    });
    // Update AI prompt
    const updateAIPrompt = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useMutation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useMutation"])({
        mutationFn: (systemPrompt)=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$business$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["businessConfigApi"].updateAIPrompt(systemPrompt, businessId),
        onSuccess: (data)=>{
            queryClient.setQueryData([
                QUERY_KEY,
                businessId
            ], data);
            toast({
                title: 'AI Prompt Updated',
                description: 'AI system prompt has been saved.'
            });
        },
        onError: (error)=>{
            toast({
                title: 'Update Failed',
                description: error.response?.data?.detail || 'Failed to update AI prompt',
                variant: 'destructive'
            });
        }
    });
    // Update WhatsApp configuration
    const updateWhatsApp = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useMutation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useMutation"])({
        mutationFn: (whatsappConfig)=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$business$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["businessConfigApi"].updateWhatsAppConfig(whatsappConfig, businessId),
        onSuccess: (data)=>{
            queryClient.setQueryData([
                QUERY_KEY,
                businessId
            ], data);
            toast({
                title: 'WhatsApp Updated',
                description: 'WhatsApp configuration has been saved.'
            });
        },
        onError: (error)=>{
            toast({
                title: 'Update Failed',
                description: error.response?.data?.detail || 'Failed to update WhatsApp config',
                variant: 'destructive'
            });
        }
    });
    return {
        config,
        isLoading,
        error,
        refetch,
        updateConfig: updateConfig.mutate,
        isUpdating: updateConfig.isPending,
        reloadConfig: reloadConfig.mutate,
        isReloading: reloadConfig.isPending,
        updateAIPrompt: updateAIPrompt.mutate,
        isUpdatingAIPrompt: updateAIPrompt.isPending,
        updateWhatsApp: updateWhatsApp.mutate,
        isUpdatingWhatsApp: updateWhatsApp.isPending
    };
}
function useAIPrompt(businessId = 'default') {
    const { data, isLoading, error } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            'aiPrompt',
            businessId
        ],
        queryFn: ()=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$business$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["businessConfigApi"].getAIPrompt(businessId),
        staleTime: 10 * 60 * 1000
    });
    return {
        systemPrompt: data?.system_prompt,
        isLoading,
        error
    };
}
function useServices(businessId = 'default') {
    const { data: services, isLoading, error } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            'services',
            businessId
        ],
        queryFn: ()=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$business$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["businessConfigApi"].getServices(businessId),
        staleTime: 5 * 60 * 1000
    });
    return {
        services: services || [],
        isLoading,
        error
    };
}
}),
"[project]/contexts/ConfigContext.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ConfigProvider",
    ()=>ConfigProvider,
    "useConfig",
    ()=>useConfig
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$use$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/hooks/use-config.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/AuthContext.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
const ConfigContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createContext"])(undefined);
const ConfigProvider = ({ children })=>{
    const { user, isAuthenticated, isLoading: authLoading } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAuth"])();
    // CRITICAL: Use tenant_id from the authenticated user to ensure each tenant has their own config cache
    // This prevents config data from being shared between different tenants in React Query's cache
    // Without this, all tenants would share the same 'default' cache key and see each other's data
    const tenantId = user?.tenant_id || 'default';
    // Only fetch config if user is authenticated
    const { config, isLoading, error, refetch } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$use$2d$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useConfig"])(tenantId, isAuthenticated);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(ConfigContext.Provider, {
        value: {
            config,
            isLoading: isLoading || authLoading,
            error,
            refreshConfig: refetch
        },
        children: children
    }, void 0, false, {
        fileName: "[project]/contexts/ConfigContext.tsx",
        lineNumber: 29,
        columnNumber: 9
    }, ("TURBOPACK compile-time value", void 0));
};
const useConfig = ()=>{
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useContext"])(ConfigContext);
    if (context === undefined) {
        throw new Error('useConfig must be used within a ConfigProvider');
    }
    return context;
};
}),
"[project]/contexts/TenantContext.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "TenantProvider",
    ()=>TenantProvider,
    "useTenant",
    ()=>useTenant
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/AuthContext.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$ConfigContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/ConfigContext.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
const TenantContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createContext"])(undefined);
function TenantProvider({ children }) {
    const { user, isLoading: authLoading } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAuth"])();
    const { config, isLoading: configLoading } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$ConfigContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useConfig"])();
    const tenantId = user?.tenant_id || null;
    const businessId = user?.business_id || user?.tenant_id || null;
    const isConfigured = config?.is_configured ?? false;
    const isLoading = authLoading || configLoading;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(TenantContext.Provider, {
        value: {
            tenantId,
            businessId,
            config,
            isConfigured,
            isLoading
        },
        children: children
    }, void 0, false, {
        fileName: "[project]/contexts/TenantContext.tsx",
        lineNumber: 28,
        columnNumber: 9
    }, this);
}
function useTenant() {
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useContext"])(TenantContext);
    if (context === undefined) {
        throw new Error('useTenant must be used within a TenantProvider');
    }
    return context;
}
}),
"[project]/components/providers.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>Providers
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$query$2d$core$2f$build$2f$modern$2f$queryClient$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/query-core/build/modern/queryClient.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/QueryClientProvider.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/AuthContext.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$ConfigContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/ConfigContext.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$TenantContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/TenantContext.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
function Providers({ children }) {
    const [queryClient] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(()=>new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$query$2d$core$2f$build$2f$modern$2f$queryClient$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["QueryClient"]({
            defaultOptions: {
                queries: {
                    staleTime: 60 * 1000,
                    retry: 1
                }
            }
        }));
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["QueryClientProvider"], {
        client: queryClient,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AuthProvider"], {
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$ConfigContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ConfigProvider"], {
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$TenantContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["TenantProvider"], {
                    children: children
                }, void 0, false, {
                    fileName: "[project]/components/providers.tsx",
                    lineNumber: 25,
                    columnNumber: 21
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/providers.tsx",
                lineNumber: 24,
                columnNumber: 17
            }, this)
        }, void 0, false, {
            fileName: "[project]/components/providers.tsx",
            lineNumber: 23,
            columnNumber: 13
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/providers.tsx",
        lineNumber: 22,
        columnNumber: 9
    }, this);
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__e8c4969e._.js.map