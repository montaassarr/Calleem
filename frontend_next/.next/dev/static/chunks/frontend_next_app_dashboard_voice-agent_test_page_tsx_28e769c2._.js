(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>VoiceAgentTestPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$livekit$2d$client$2f$dist$2f$livekit$2d$client$2e$esm$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/livekit-client/dist/livekit-client.esm.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__R__as__RoomAudioRenderer$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/@livekit/components-react/dist/components-CMpq9Z_u.mjs [app-client] (ecmascript) <export R as RoomAudioRenderer>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__z__as__SessionProvider$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/@livekit/components-react/dist/components-CMpq9Z_u.mjs [app-client] (ecmascript) <export z as SessionProvider>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__q__as__StartAudio$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/@livekit/components-react/dist/components-CMpq9Z_u.mjs [app-client] (ecmascript) <export q as StartAudio>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$hooks$2d$CA8cirWq$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__a3__as__useSession$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/@livekit/components-react/dist/hooks-CA8cirWq.mjs [app-client] (ecmascript) <export a3 as useSession>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$contexts$2d$CjCD4TaH$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__aB__as__useSessionContext$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/@livekit/components-react/dist/contexts-CjCD4TaH.mjs [app-client] (ecmascript) <export aB as useSessionContext>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/contexts/AuthContext.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature(), _s2 = __turbopack_context__.k.signature();
'use client';
;
;
;
;
/**
 * Voice Agent Test Page
 * Multi-tenant LiveKit voice agent for testing
 */ function VoiceAgentUI({ tenantId }) {
    _s();
    const { isConnected, start, end, agentState, roomName } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$contexts$2d$CjCD4TaH$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__aB__as__useSessionContext$3e$__["useSessionContext"])();
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-col items-center justify-center min-h-[80vh] p-8",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mb-8 text-center",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                        className: "text-3xl font-bold mb-2",
                        children: "AI Voice Agent Test"
                    }, void 0, false, {
                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                        lineNumber: 26,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-muted-foreground",
                        children: [
                            "Tenant: ",
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("code", {
                                className: "bg-muted px-2 py-1 rounded",
                                children: tenantId
                            }, void 0, false, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 28,
                                columnNumber: 19
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                        lineNumber: 27,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 25,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mb-8",
                children: isConnected ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex items-center gap-2 text-green-600",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "h-3 w-3 bg-green-600 rounded-full animate-pulse"
                        }, void 0, false, {
                            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                            lineNumber: 36,
                            columnNumber: 13
                        }, this),
                        "Connected - Speak to your AI receptionist"
                    ]
                }, void 0, true, {
                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                    lineNumber: 35,
                    columnNumber: 11
                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex items-center gap-2 text-muted-foreground",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "h-3 w-3 bg-gray-400 rounded-full"
                        }, void 0, false, {
                            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                            lineNumber: 41,
                            columnNumber: 13
                        }, this),
                        "Click Start Call to begin"
                    ]
                }, void 0, true, {
                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                    lineNumber: 40,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 33,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex gap-4 mb-8",
                children: !isConnected ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    onClick: ()=>start(),
                    className: "px-8 py-4 bg-primary text-primary-foreground rounded-full text-lg font-semibold hover:bg-primary/90 transition-all shadow-lg",
                    children: "🎤 Start Call"
                }, void 0, false, {
                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                    lineNumber: 50,
                    columnNumber: 11
                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    onClick: ()=>end(),
                    className: "px-8 py-4 bg-red-600 text-white rounded-full text-lg font-semibold hover:bg-red-700 transition-all shadow-lg",
                    children: "📴 End Call"
                }, void 0, false, {
                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                    lineNumber: 57,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 48,
                columnNumber: 7
            }, this),
            isConnected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "bg-muted/50 rounded-xl p-6 w-full max-w-md",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                        className: "font-semibold mb-3",
                        children: "Agent Status"
                    }, void 0, false, {
                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                        lineNumber: 69,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "space-y-2 text-sm",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "flex justify-between",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "text-muted-foreground",
                                        children: "State:"
                                    }, void 0, false, {
                                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                        lineNumber: 72,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "font-medium capitalize",
                                        children: agentState || 'initializing'
                                    }, void 0, false, {
                                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                        lineNumber: 73,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 71,
                                columnNumber: 13
                            }, this),
                            roomName && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "flex justify-between",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "text-muted-foreground",
                                        children: "Room:"
                                    }, void 0, false, {
                                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                        lineNumber: 77,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "font-mono text-xs",
                                        children: roomName
                                    }, void 0, false, {
                                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                        lineNumber: 78,
                                        columnNumber: 17
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 76,
                                columnNumber: 15
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                        lineNumber: 70,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 68,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-8 text-center text-sm text-muted-foreground max-w-md",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "mb-2",
                        children: "💡 Try saying:"
                    }, void 0, false, {
                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                        lineNumber: 87,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("ul", {
                        className: "space-y-1",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                children: '"I\'d like to book an appointment"'
                            }, void 0, false, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 89,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                children: '"What services do you offer?"'
                            }, void 0, false, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 90,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                children: '"Are you open tomorrow?"'
                            }, void 0, false, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 91,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                        lineNumber: 88,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 86,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
        lineNumber: 23,
        columnNumber: 5
    }, this);
}
_s(VoiceAgentUI, "SUXmljwp5gLvk/pBhhhd7Be8WeE=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$contexts$2d$CjCD4TaH$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__aB__as__useSessionContext$3e$__["useSessionContext"]
    ];
});
_c = VoiceAgentUI;
function VoiceAgentSession({ tenantId }) {
    _s1();
    // Use TokenSource.custom() for proper POST body handling
    const tokenSource = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "VoiceAgentSession.useMemo[tokenSource]": ()=>{
            return __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$livekit$2d$client$2f$dist$2f$livekit$2d$client$2e$esm$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["TokenSource"].custom({
                "VoiceAgentSession.useMemo[tokenSource]": async ()=>{
                    const res = await fetch('/api/connection-details', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            tenant_id: tenantId
                        })
                    });
                    if (!res.ok) {
                        const errorText = await res.text();
                        throw new Error(`Failed to get connection details: ${errorText}`);
                    }
                    return await res.json();
                }
            }["VoiceAgentSession.useMemo[tokenSource]"]);
        }
    }["VoiceAgentSession.useMemo[tokenSource]"], [
        tenantId
    ]);
    // Create session from tokenSource
    const session = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$hooks$2d$CA8cirWq$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__a3__as__useSession$3e$__["useSession"])(tokenSource);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__z__as__SessionProvider$3e$__["SessionProvider"], {
        session: session,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(VoiceAgentUI, {
                tenantId: tenantId
            }, void 0, false, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 122,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__q__as__StartAudio$3e$__["StartAudio"], {
                label: "Enable Audio"
            }, void 0, false, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 123,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__R__as__RoomAudioRenderer$3e$__["RoomAudioRenderer"], {}, void 0, false, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 124,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
        lineNumber: 121,
        columnNumber: 5
    }, this);
}
_s1(VoiceAgentSession, "Q++Z3a8kOPsck1U/YcJpzsm+06E=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$hooks$2d$CA8cirWq$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__a3__as__useSession$3e$__["useSession"]
    ];
});
_c1 = VoiceAgentSession;
function VoiceAgentTestPage() {
    _s2();
    const { user, isLoading } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAuth"])();
    const [mounted, setMounted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "VoiceAgentTestPage.useEffect": ()=>{
            setMounted(true);
        }
    }["VoiceAgentTestPage.useEffect"], []);
    if (!mounted || isLoading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex items-center justify-center h-screen",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "animate-spin rounded-full h-12 w-12 border-b-2 border-primary"
            }, void 0, false, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 140,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
            lineNumber: 139,
            columnNumber: 7
        }, this);
    }
    if (!user?.tenant_id) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex flex-col items-center justify-center h-screen",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                    className: "text-2xl font-bold mb-4",
                    children: "No Tenant Found"
                }, void 0, false, {
                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                    lineNumber: 148,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: "text-muted-foreground",
                    children: "Please log in to test the voice agent."
                }, void 0, false, {
                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                    lineNumber: 149,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
            lineNumber: 147,
            columnNumber: 7
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(VoiceAgentSession, {
        tenantId: user.tenant_id
    }, void 0, false, {
        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
        lineNumber: 154,
        columnNumber: 10
    }, this);
}
_s2(VoiceAgentTestPage, "eSFTNhzcndhl1O9TUUpTUdk1wpQ=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAuth"]
    ];
});
_c2 = VoiceAgentTestPage;
var _c, _c1, _c2;
__turbopack_context__.k.register(_c, "VoiceAgentUI");
__turbopack_context__.k.register(_c1, "VoiceAgentSession");
__turbopack_context__.k.register(_c2, "VoiceAgentTestPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=frontend_next_app_dashboard_voice-agent_test_page_tsx_28e769c2._.js.map