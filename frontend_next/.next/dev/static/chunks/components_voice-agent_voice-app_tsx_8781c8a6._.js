(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/components/voice-agent/voice-app.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "VoiceApp",
    ()=>VoiceApp
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$room$2d$BH8Rm3Ha$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__L__as__LiveKitRoom$3e$__ = __turbopack_context__.i("[project]/node_modules/@livekit/components-react/dist/room-BH8Rm3Ha.mjs [app-client] (ecmascript) <export L as LiveKitRoom>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__R__as__RoomAudioRenderer$3e$__ = __turbopack_context__.i("[project]/node_modules/@livekit/components-react/dist/components-CMpq9Z_u.mjs [app-client] (ecmascript) <export R as RoomAudioRenderer>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__q__as__StartAudio$3e$__ = __turbopack_context__.i("[project]/node_modules/@livekit/components-react/dist/components-CMpq9Z_u.mjs [app-client] (ecmascript) <export q as StartAudio>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$hooks$2d$CA8cirWq$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__X__as__useVoiceAssistant$3e$__ = __turbopack_context__.i("[project]/node_modules/@livekit/components-react/dist/hooks-CA8cirWq.mjs [app-client] (ecmascript) <export X as useVoiceAssistant>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__B__as__BarVisualizer$3e$__ = __turbopack_context__.i("[project]/node_modules/@livekit/components-react/dist/components-CMpq9Z_u.mjs [app-client] (ecmascript) <export B as BarVisualizer>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$prefabs$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@livekit/components-react/dist/prefabs.mjs [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
'use client';
;
;
function VoiceApp({ token, serverUrl, onDisconnect, agentName }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$room$2d$BH8Rm3Ha$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__L__as__LiveKitRoom$3e$__["LiveKitRoom"], {
        token: token,
        serverUrl: serverUrl,
        connect: true,
        audio: true,
        video: false,
        onDisconnected: onDisconnect,
        className: "h-full w-full",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(SimpleVoiceAssistant, {
                agentName: agentName
            }, void 0, false, {
                fileName: "[project]/components/voice-agent/voice-app.tsx",
                lineNumber: 32,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "fixed top-4 left-1/2 transform -translate-x-1/2 z-50",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__q__as__StartAudio$3e$__["StartAudio"], {
                    label: "🔊 Click HERE to Enable Audio & Hear AI Voice",
                    className: "bg-green-500 hover:bg-green-600 text-white font-bold px-6 py-3 rounded-lg shadow-lg animate-pulse"
                }, void 0, false, {
                    fileName: "[project]/components/voice-agent/voice-app.tsx",
                    lineNumber: 34,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/voice-agent/voice-app.tsx",
                lineNumber: 33,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__R__as__RoomAudioRenderer$3e$__["RoomAudioRenderer"], {}, void 0, false, {
                fileName: "[project]/components/voice-agent/voice-app.tsx",
                lineNumber: 39,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/voice-agent/voice-app.tsx",
        lineNumber: 23,
        columnNumber: 5
    }, this);
}
_c = VoiceApp;
function SimpleVoiceAssistant({ agentName }) {
    _s();
    const { state, audioTrack } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$hooks$2d$CA8cirWq$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__X__as__useVoiceAssistant$3e$__["useVoiceAssistant"])();
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "flex flex-col items-center justify-center h-full p-8 space-y-6",
        children: [
            !audioTrack && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "bg-yellow-100 dark:bg-yellow-900 border-2 border-yellow-500 rounded-lg p-4 max-w-md text-center",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-yellow-800 dark:text-yellow-200 font-semibold mb-2",
                        children: "🔊 Can't Hear the AI?"
                    }, void 0, false, {
                        fileName: "[project]/components/voice-agent/voice-app.tsx",
                        lineNumber: 52,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-sm text-yellow-700 dark:text-yellow-300",
                        children: 'Look for the green "Enable Audio" button at the top and click it!'
                    }, void 0, false, {
                        fileName: "[project]/components/voice-agent/voice-app.tsx",
                        lineNumber: 55,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/voice-agent/voice-app.tsx",
                lineNumber: 51,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "text-center space-y-2",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                        className: "text-lg font-semibold",
                        children: [
                            state === 'connecting' && '🔌 Connecting to agent...',
                            state === 'initializing' && '⚙️ Initializing...',
                            state === 'listening' && '👂 Listening...',
                            state === 'thinking' && '🤔 Thinking...',
                            state === 'speaking' && '🗣️ Speaking...',
                            state === 'disconnected' && '❌ Disconnected'
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/voice-agent/voice-app.tsx",
                        lineNumber: 62,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-sm text-muted-foreground",
                        children: agentName && `Agent: ${agentName}`
                    }, void 0, false, {
                        fileName: "[project]/components/voice-agent/voice-app.tsx",
                        lineNumber: 70,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/voice-agent/voice-app.tsx",
                lineNumber: 61,
                columnNumber: 7
            }, this),
            audioTrack && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "w-full max-w-md",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$components$2d$CMpq9Z_u$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__B__as__BarVisualizer$3e$__["BarVisualizer"], {
                    state: state,
                    barCount: 7,
                    trackRef: audioTrack,
                    className: "h-32",
                    options: {
                        minHeight: 30
                    }
                }, void 0, false, {
                    fileName: "[project]/components/voice-agent/voice-app.tsx",
                    lineNumber: 77,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/voice-agent/voice-app.tsx",
                lineNumber: 76,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$prefabs$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["VoiceAssistantControlBar"], {}, void 0, false, {
                fileName: "[project]/components/voice-agent/voice-app.tsx",
                lineNumber: 87,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "mt-auto text-center space-y-2 text-sm text-muted-foreground max-w-lg",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "font-semibold",
                        children: "💡 Quick Tips:"
                    }, void 0, false, {
                        fileName: "[project]/components/voice-agent/voice-app.tsx",
                        lineNumber: 91,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("ul", {
                        className: "text-xs space-y-1",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                children: "• Click the green button above if you can't hear AI"
                            }, void 0, false, {
                                fileName: "[project]/components/voice-agent/voice-app.tsx",
                                lineNumber: 93,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                children: "• Allow microphone access when prompted"
                            }, void 0, false, {
                                fileName: "[project]/components/voice-agent/voice-app.tsx",
                                lineNumber: 94,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                children: '• Speak clearly: "I\'d like to book an appointment"'
                            }, void 0, false, {
                                fileName: "[project]/components/voice-agent/voice-app.tsx",
                                lineNumber: 95,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                children: "• AI will respond with voice and book for you"
                            }, void 0, false, {
                                fileName: "[project]/components/voice-agent/voice-app.tsx",
                                lineNumber: 96,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/voice-agent/voice-app.tsx",
                        lineNumber: 92,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/voice-agent/voice-app.tsx",
                lineNumber: 90,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/voice-agent/voice-app.tsx",
        lineNumber: 48,
        columnNumber: 5
    }, this);
}
_s(SimpleVoiceAssistant, "j4tAc3C/JJbHjgL3PIoaZKEQa5E=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$livekit$2f$components$2d$react$2f$dist$2f$hooks$2d$CA8cirWq$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__X__as__useVoiceAssistant$3e$__["useVoiceAssistant"]
    ];
});
_c1 = SimpleVoiceAssistant;
var _c, _c1;
__turbopack_context__.k.register(_c, "VoiceApp");
__turbopack_context__.k.register(_c1, "SimpleVoiceAssistant");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/voice-agent/voice-app.tsx [app-client] (ecmascript, next/dynamic entry)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/components/voice-agent/voice-app.tsx [app-client] (ecmascript)"));
}),
]);

//# sourceMappingURL=components_voice-agent_voice-app_tsx_8781c8a6._.js.map