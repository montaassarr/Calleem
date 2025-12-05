module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

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
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/node:buffer [external] (node:buffer, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("node:buffer", () => require("node:buffer"));

module.exports = mod;
}),
"[externals]/node:crypto [external] (node:crypto, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("node:crypto", () => require("node:crypto"));

module.exports = mod;
}),
"[externals]/node:util [external] (node:util, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("node:util", () => require("node:util"));

module.exports = mod;
}),
"[project]/frontend_next/app/api/connection-details/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "POST",
    ()=>POST,
    "revalidate",
    ()=>revalidate
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$livekit$2d$server$2d$sdk$2f$dist$2f$index$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/livekit-server-sdk/dist/index.js [app-route] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$livekit$2d$server$2d$sdk$2f$dist$2f$AccessToken$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/livekit-server-sdk/dist/AccessToken.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$protocol$2f$dist$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/@livekit/protocol/dist/index.mjs [app-route] (ecmascript) <locals>");
;
;
;
const API_KEY = process.env.LIVEKIT_API_KEY;
const API_SECRET = process.env.LIVEKIT_API_SECRET;
const LIVEKIT_URL = process.env.LIVEKIT_URL;
const revalidate = 0;
async function POST(req) {
    try {
        if (!LIVEKIT_URL || !API_KEY || !API_SECRET) {
            throw new Error('LiveKit configuration missing. Check LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET');
        }
        const body = await req.json();
        const tenantId = body?.tenant_id;
        const agentName = body?.room_config?.agents?.[0]?.agent_name;
        if (!tenantId) {
            throw new Error('tenant_id is required');
        }
        // Generate room name with tenant prefix for agent to extract
        const participantName = 'user';
        const participantIdentity = `user_${Math.floor(Math.random() * 10_000)}`;
        const roomName = `preview-${tenantId}-${Math.floor(Math.random() * 10_000)}`;
        // Room metadata for agent to identify tenant
        const roomMetadata = JSON.stringify({
            tenant_id: tenantId
        });
        const participantToken = await createParticipantToken({
            identity: participantIdentity,
            name: participantName
        }, roomName, roomMetadata, agentName);
        const data = {
            serverUrl: LIVEKIT_URL,
            roomName,
            participantToken,
            participantName
        };
        return __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(data, {
            headers: {
                'Cache-Control': 'no-store'
            }
        });
    } catch (error) {
        console.error('Connection details error:', error);
        return new __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"](error instanceof Error ? error.message : 'Internal error', {
            status: 500
        });
    }
}
async function createParticipantToken(userInfo, roomName, roomMetadata, agentName) {
    const at = new __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$livekit$2d$server$2d$sdk$2f$dist$2f$AccessToken$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["AccessToken"](API_KEY, API_SECRET, {
        ...userInfo,
        ttl: '15m'
    });
    const grant = {
        room: roomName,
        roomJoin: true,
        roomCreate: true,
        canPublish: true,
        canPublishData: true,
        canSubscribe: true
    };
    at.addGrant(grant);
    // Set room metadata with tenant info
    at.metadata = roomMetadata;
    if (agentName) {
        at.roomConfig = new __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$protocol$2f$dist$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$locals$3e$__["RoomConfiguration"]({
            agents: [
                {
                    agentName
                }
            ]
        });
    }
    return at.toJwt();
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__c0a8efc9._.js.map