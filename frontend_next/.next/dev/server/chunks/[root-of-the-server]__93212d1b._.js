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
"[project]/app/api/connection-details/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "POST",
    ()=>POST,
    "revalidate",
    ()=>revalidate
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/server.js [app-route] (ecmascript)");
;
const revalidate = 0;
async function POST(req) {
    try {
        // Get authentication token from Authorization header (client will pass from localStorage)
        const authHeader = req.headers.get('authorization');
        const token = authHeader?.replace('Bearer ', '') || req.cookies.get('access_token')?.value || req.cookies.get('token')?.value;
        if (!token) {
            console.error('No authentication token found');
            return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"]('Unauthorized - Please log in', {
                status: 401
            });
        }
        // Parse request body for agent configuration
        const body = await req.json();
        const agentName = body?.room_config?.agents?.[0]?.agent_name;
        console.log('Creating LiveKit session...');
        // Call your backend API to create LiveKit session
        const backendUrl = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://localhost:8000';
        const response = await fetch(`${backendUrl}/api/v1/voice-agent/webrtc/test`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                room_name: body.roomName,
                identity: body.identity
            })
        });
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend error:', errorText);
            return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"](`Backend error: ${errorText}`, {
                status: response.status
            });
        }
        const sessionData = await response.json();
        console.log('Backend response:', sessionData);
        // Transform backend response to match LiveKit frontend expectations
        const connectionDetails = {
            serverUrl: sessionData.url || sessionData.server_url || sessionData.serverUrl,
            roomName: sessionData.room_name || sessionData.roomName,
            participantToken: sessionData.token || sessionData.participantToken,
            participantName: sessionData.identity || body.identity || 'user'
        };
        // Validate all required fields are present
        if (!connectionDetails.serverUrl) {
            console.error('Missing serverUrl in backend response:', sessionData);
            return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"]('Backend did not return a valid server URL', {
                status: 500
            });
        }
        if (!connectionDetails.roomName) {
            console.error('Missing roomName in backend response:', sessionData);
            return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"]('Backend did not return a valid room name', {
                status: 500
            });
        }
        if (!connectionDetails.participantToken) {
            console.error('Missing participantToken in backend response:', sessionData);
            return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"]('Backend did not return a valid access token', {
                status: 500
            });
        }
        console.log('Returning connection details:', {
            serverUrl: connectionDetails.serverUrl,
            roomName: connectionDetails.roomName,
            participantName: connectionDetails.participantName,
            tokenLength: connectionDetails.participantToken?.length
        });
        const headers = new Headers({
            'Cache-Control': 'no-store'
        });
        return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(connectionDetails, {
            headers
        });
    } catch (error) {
        console.error('Connection details error:', error);
        if (error instanceof Error) {
            return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"](error.message, {
                status: 500
            });
        }
        return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"]('Internal server error', {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__93212d1b._.js.map