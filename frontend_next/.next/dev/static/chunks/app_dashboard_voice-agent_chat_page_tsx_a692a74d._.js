(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/app/dashboard/voice-agent/chat/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>VoiceAgentChatPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
'use client';
;
function VoiceAgentChatPage() {
    // Configure the LiveKit voice agent with your multi-tenant settings
    const appConfig = {
        companyName: 'AI Receptionist',
        pageTitle: 'AI Receptionist - Voice Chat',
        pageDescription: 'Talk to your AI receptionist for appointment booking and inquiries',
        supportsChatInput: true,
        supportsVideoInput: false,
        supportsScreenShare: false,
        isPreConnectBufferEnabled: true,
        logo: '/logo.svg',
        accent: '#002cf2',
        logoDark: '/logo.svg',
        accentDark: '#1fd5f9',
        startButtonText: 'Start Chat'
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "h-screen w-full bg-background",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(App, {
            appConfig: appConfig
        }, void 0, false, {
            fileName: "[project]/app/dashboard/voice-agent/chat/page.tsx",
            lineNumber: 27,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/app/dashboard/voice-agent/chat/page.tsx",
        lineNumber: 26,
        columnNumber: 5
    }, this);
}
_c = VoiceAgentChatPage;
var _c;
__turbopack_context__.k.register(_c, "VoiceAgentChatPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=app_dashboard_voice-agent_chat_page_tsx_a692a74d._.js.map