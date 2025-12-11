module.exports = [
"[project]/frontend_next/components/vapi/VapiProvider.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "VapiProvider",
    ()=>VapiProvider,
    "useVapi",
    ()=>useVapi
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$vapi$2d$ai$2f$web$2f$dist$2f$vapi$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/@vapi-ai/web/dist/vapi.js [app-ssr] (ecmascript)");
"use client";
;
;
;
const VapiContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createContext"])(null);
function VapiProvider({ children, apiKey }) {
    const [vapi, setVapi] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [status, setStatus] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('disconnected');
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (!apiKey) return;
        const vapiInstance = new __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f40$vapi$2d$ai$2f$web$2f$dist$2f$vapi$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"](apiKey);
        setVapi(vapiInstance);
        // Event listeners
        vapiInstance.on('call-start', ()=>setStatus('connected'));
        vapiInstance.on('call-end', ()=>setStatus('disconnected'));
        vapiInstance.on('error', (e)=>{
            console.error('Vapi Error:', e);
            setStatus('disconnected');
        });
        return ()=>{
            vapiInstance.stop();
        };
    }, [
        apiKey
    ]);
    const startCall = async (assistantId)=>{
        if (!vapi) return;
        setStatus('connecting');
        try {
            if (assistantId) {
                await vapi.start(assistantId);
            } else {
                // Start transient call or default? 
                // Usually we start with assistant ID
                console.warn("No assistant ID provided to startCall in VapiProvider");
                setStatus('disconnected');
            }
        } catch (e) {
            console.error("Failed to start call", e);
            setStatus('disconnected');
        }
    };
    const stopCall = ()=>{
        if (!vapi) return;
        vapi.stop();
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(VapiContext.Provider, {
        value: {
            vapi,
            isSessionActive: status === 'connected',
            startCall,
            stopCall,
            status
        },
        children: children
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/vapi/VapiProvider.tsx",
        lineNumber: 63,
        columnNumber: 9
    }, this);
}
function useVapi() {
    const context = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useContext"])(VapiContext);
    if (!context) {
        throw new Error('useVapi must be used within a VapiProvider');
    }
    return context;
}
}),
"[project]/frontend_next/components/vapi/CallButton.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "CallButton",
    ()=>CallButton
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$vapi$2f$VapiProvider$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/components/vapi/VapiProvider.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/components/ui/button.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/lucide-react/dist/esm/icons/mic.js [app-ssr] (ecmascript) <export default as Mic>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$phone$2d$off$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__PhoneOff$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/lucide-react/dist/esm/icons/phone-off.js [app-ssr] (ecmascript) <export default as PhoneOff>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$loader$2d$circle$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Loader2$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/lucide-react/dist/esm/icons/loader-circle.js [app-ssr] (ecmascript) <export default as Loader2>");
"use client";
;
;
;
;
function CallButton({ assistantId, onCallStart, onCallEnd, className }) {
    const { startCall, stopCall, status } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$vapi$2f$VapiProvider$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useVapi"])();
    const handleToggleCall = async ()=>{
        if (status === 'connected' || status === 'connecting') {
            stopCall();
            if (onCallEnd) onCallEnd();
        } else {
            if (onCallStart) onCallStart();
            await startCall(assistantId);
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Button"], {
        onClick: handleToggleCall,
        variant: status === 'connected' ? "destructive" : "default",
        size: "lg",
        className: `gap-2 min-w-[150px] ${className}`,
        disabled: status === 'connecting',
        children: status === 'connecting' ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$loader$2d$circle$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Loader2$3e$__["Loader2"], {
                    className: "h-4 w-4 animate-spin"
                }, void 0, false, {
                    fileName: "[project]/frontend_next/components/vapi/CallButton.tsx",
                    lineNumber: 38,
                    columnNumber: 21
                }, this),
                "Connecting..."
            ]
        }, void 0, true) : status === 'connected' ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$phone$2d$off$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__PhoneOff$3e$__["PhoneOff"], {
                    className: "h-4 w-4"
                }, void 0, false, {
                    fileName: "[project]/frontend_next/components/vapi/CallButton.tsx",
                    lineNumber: 43,
                    columnNumber: 21
                }, this),
                "End Call"
            ]
        }, void 0, true) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__["Mic"], {
                    className: "h-4 w-4"
                }, void 0, false, {
                    fileName: "[project]/frontend_next/components/vapi/CallButton.tsx",
                    lineNumber: 48,
                    columnNumber: 21
                }, this),
                "Start Call"
            ]
        }, void 0, true)
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/vapi/CallButton.tsx",
        lineNumber: 29,
        columnNumber: 9
    }, this);
}
}),
"[project]/frontend_next/lib/api-endpoints.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "apiEndpoints",
    ()=>apiEndpoints,
    "appointmentsApi",
    ()=>appointmentsApi,
    "conversationsApi",
    ()=>conversationsApi,
    "servicesApi",
    ()=>servicesApi,
    "usersApi",
    ()=>usersApi,
    "vapiApi",
    ()=>vapiApi,
    "webhookApi",
    ()=>webhookApi
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/lib/api.ts [app-ssr] (ecmascript)");
;
// API Base URL for direct fetch calls
const BASE_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api/v1`;
const appointmentsApi = {
    list: async (filters)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get("/appointments/", {
            params: filters
        });
        return response;
    },
    get: async (appointmentId)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get(`/appointments/${appointmentId}`);
        return response;
    },
    create: async (data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post("/appointments/", data);
        return response;
    },
    update: async (appointmentId, data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put(`/appointments/${appointmentId}`, data);
        return response;
    },
    delete: async (appointmentId)=>{
        await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].delete(`/appointments/${appointmentId}`);
    },
    cancel: async (appointmentId)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post(`/appointments/${appointmentId}/cancel`);
        return response;
    },
    checkAvailability: async (date, time, durationMinutes = 30)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get("/appointments/availability/check", {
            params: {
                date,
                time,
                duration_minutes: durationMinutes
            }
        });
        return response;
    },
    getStats: async ()=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get("/appointments/stats/summary");
        return response;
    }
};
const servicesApi = {
    list: async (filters)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get("/services/", {
            params: filters
        });
        return response;
    },
    get: async (serviceId)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get(`/services/${serviceId}`);
        return response;
    },
    create: async (data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post("/services/", data);
        return response;
    },
    update: async (serviceId, data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put(`/services/${serviceId}`, data);
        return response;
    },
    delete: async (serviceId)=>{
        await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].delete(`/services/${serviceId}`);
    },
    getActive: async ()=>{
        return servicesApi.list({
            active_only: true
        });
    },
    toggleActive: async (serviceId, isActive)=>{
        return servicesApi.update(serviceId, {
            active: isActive
        });
    }
};
const conversationsApi = {
    list: async (params)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get("/conversations", {
            params
        });
        return response;
    },
    get: async (id)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get(`/conversations/${id}`);
        return response;
    },
    delete: async (id)=>{
        await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].delete(`/conversations/${id}`);
    }
};
const webhookApi = {
    getStatus: async ()=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get("/whatsapp/status");
        return response;
    },
    updateSettings: async (settings)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post("/whatsapp/settings", settings);
        return response;
    }
};
const usersApi = {
    list: async (tenantId)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get("/admin/users", {
            params: {
                tenant_id: tenantId
            }
        });
        return response;
    },
    create: async (data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post("/admin/users", data);
        return response;
    },
    delete: async (id)=>{
        await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].delete(`/admin/users/${id}`);
    }
};
const apiEndpoints = {
    agents: {
        getMyAgent: ()=>`${API_BASE_URL}/agents/my-agent`,
        updateMyAgent: ()=>`${API_BASE_URL}/agents/my-agent`,
        // Deprecated: Old multi-agent endpoints kept for backward compatibility
        list: ()=>`${API_BASE_URL}/agents`,
        get: (id)=>`${API_BASE_URL}/agents/${id}`,
        create: ()=>`${API_BASE_URL}/agents`,
        update: (id)=>`${API_BASE_URL}/agents/${id}`,
        delete: (id)=>`${API_BASE_URL}/agents/${id}`
    },
    voiceAgent: {
        // Temporarily keep but point to Vapi stats if possible, or dead endpoint
        stats: ()=>`${API_BASE_URL}/voice-agent/stats`,
        phoneNumbers: ()=>`${API_BASE_URL}/voice-agent/numbers`,
        searchNumbers: ()=>`${API_BASE_URL}/voice-agent/search-numbers`,
        purchaseNumber: ()=>`${API_BASE_URL}/voice-agent/purchase-number`
    },
    phoneNumbers: {
        test: ()=>`${API_BASE_URL}/phone-numbers/test`,
        search: ()=>`${API_BASE_URL}/phone-numbers/search`,
        purchase: ()=>`${API_BASE_URL}/phone-numbers/purchase`,
        list: ()=>`${API_BASE_URL}/phone-numbers/list`,
        assign: (id)=>`${API_BASE_URL}/phone-numbers/${id}/assign`,
        delete: (id)=>`${API_BASE_URL}/phone-numbers/${id}`
    },
    onboarding: {
        getStatus: ()=>`${API_BASE_URL}/onboarding/status`,
        skipOnboarding: ()=>`${API_BASE_URL}/onboarding/skip`
    },
    vapi: {
        createAssistant: (tenantId)=>`${API_BASE_URL}/vapi/tenants/${tenantId}/assistant`,
        updateAssistant: (tenantId, assistantId)=>`${API_BASE_URL}/vapi/tenants/${tenantId}/assistant/${assistantId}`,
        getAssistant: (tenantId)=>`${API_BASE_URL}/vapi/tenants/${tenantId}/assistant`,
        // 'Me' endpoints
        getMyAssistant: ()=>`${API_BASE_URL}/vapi/assistant/me`,
        createMyAssistant: ()=>`${API_BASE_URL}/vapi/assistant/me`,
        updateMyAssistant: ()=>`${API_BASE_URL}/vapi/assistant/me`
    }
};
const vapiApi = {
    // ... Direct tenant methods ...
    createAssistant: async (tenantId, data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post(`/vapi/tenants/${tenantId}/assistant`, data);
        return response;
    },
    updateAssistant: async (tenantId, assistantId, data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put(`/vapi/tenants/${tenantId}/assistant/${assistantId}`, data);
        return response;
    },
    getAssistant: async (tenantId)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get(`/vapi/tenants/${tenantId}/assistant`);
        return response;
    },
    // 'Me' methods
    getMyAssistant: async ()=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].get(`/vapi/assistant/me`);
        return response;
    },
    createMyAssistant: async (data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].post(`/vapi/assistant/me`, data);
        return response;
    },
    updateMyAssistant: async (data)=>{
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].put(`/vapi/assistant/me`, data);
        return response;
    }
};
}),
"[project]/frontend_next/components/ui/card.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Card",
    ()=>Card,
    "CardAction",
    ()=>CardAction,
    "CardContent",
    ()=>CardContent,
    "CardDescription",
    ()=>CardDescription,
    "CardFooter",
    ()=>CardFooter,
    "CardHeader",
    ()=>CardHeader,
    "CardTitle",
    ()=>CardTitle
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/lib/utils.ts [app-ssr] (ecmascript)");
;
;
function Card({ className, ...props }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-slot": "card",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])('bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm', className),
        ...props
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/ui/card.tsx",
        lineNumber: 7,
        columnNumber: 5
    }, this);
}
function CardHeader({ className, ...props }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-slot": "card-header",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])('@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6', className),
        ...props
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/ui/card.tsx",
        lineNumber: 20,
        columnNumber: 5
    }, this);
}
function CardTitle({ className, ...props }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-slot": "card-title",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])('leading-none font-semibold', className),
        ...props
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/ui/card.tsx",
        lineNumber: 33,
        columnNumber: 5
    }, this);
}
function CardDescription({ className, ...props }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-slot": "card-description",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])('text-muted-foreground text-sm', className),
        ...props
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/ui/card.tsx",
        lineNumber: 43,
        columnNumber: 5
    }, this);
}
function CardAction({ className, ...props }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-slot": "card-action",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])('col-start-2 row-span-2 row-start-1 self-start justify-self-end', className),
        ...props
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/ui/card.tsx",
        lineNumber: 53,
        columnNumber: 5
    }, this);
}
function CardContent({ className, ...props }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-slot": "card-content",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])('px-6', className),
        ...props
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/ui/card.tsx",
        lineNumber: 66,
        columnNumber: 5
    }, this);
}
function CardFooter({ className, ...props }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-slot": "card-footer",
        className: (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$utils$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["cn"])('flex items-center px-6 [.border-t]:pt-6', className),
        ...props
    }, void 0, false, {
        fileName: "[project]/frontend_next/components/ui/card.tsx",
        lineNumber: 76,
        columnNumber: 5
    }, this);
}
;
}),
"[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>VoiceAgentTestPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$vapi$2f$VapiProvider$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/components/vapi/VapiProvider.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$vapi$2f$CallButton$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/components/vapi/CallButton.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/contexts/AuthContext.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2d$endpoints$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/lib/api-endpoints.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/components/ui/card.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$loader$2d$circle$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Loader2$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/lucide-react/dist/esm/icons/loader-circle.js [app-ssr] (ecmascript) <export default as Loader2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/lucide-react/dist/esm/icons/mic.js [app-ssr] (ecmascript) <export default as Mic>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/lucide-react/dist/esm/icons/settings.js [app-ssr] (ecmascript) <export default as Settings>");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/components/ui/button.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend_next/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
;
;
;
;
function VoiceAgentTestPage() {
    const { user, isLoading: authLoading } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAuth"])();
    const [assistantId, setAssistantId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [configLoading, setConfigLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    // Get Vapi Public Key from env
    const apiKey = ("TURBOPACK compile-time value", "1f432dbe-7cab-496e-93e3-a348408f6726") || "";
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        async function fetchAssistant() {
            if (!user) return;
            try {
                const data = await __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$lib$2f$api$2d$endpoints$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["vapiApi"].getMyAssistant();
                if (data && data.assistant_id) {
                    setAssistantId(data.assistant_id);
                } else {
                    setError("No assistant configured");
                }
            } catch (err) {
                console.error("Failed to fetch assistant", err);
                setError("Failed to load assistant configuration");
            } finally{
                setConfigLoading(false);
            }
        }
        if (!authLoading && user) {
            fetchAssistant();
        }
    }, [
        user,
        authLoading
    ]);
    if (authLoading || configLoading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex items-center justify-center h-[calc(100vh-4rem)]",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$loader$2d$circle$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Loader2$3e$__["Loader2"], {
                className: "h-12 w-12 animate-spin text-primary"
            }, void 0, false, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 48,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
            lineNumber: 47,
            columnNumber: 7
        }, this);
    }
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$vapi$2f$VapiProvider$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["VapiProvider"], {
        apiKey: apiKey,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "flex flex-col items-center justify-center h-[calc(100vh-4rem)] bg-gradient-to-b from-background to-muted/20 p-6",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Card"], {
                className: "w-full max-w-md shadow-lg border-primary/20",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CardHeader"], {
                        className: "text-center pb-2",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "mx-auto bg-primary/10 p-4 rounded-full mb-4 w-20 h-20 flex items-center justify-center",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__["Mic"], {
                                    className: "h-10 w-10 text-primary"
                                }, void 0, false, {
                                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                    lineNumber: 70,
                                    columnNumber: 15
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 69,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CardTitle"], {
                                className: "text-2xl",
                                children: "Test Your AI Receptionist"
                            }, void 0, false, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 72,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CardDescription"], {
                                children: assistantId ? "Microphone access is required. Speak normally." : "No assistant configured yet."
                            }, void 0, false, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 73,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                        lineNumber: 68,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$card$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CardContent"], {
                        className: "flex flex-col items-center gap-6 pt-6",
                        children: error ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "text-center space-y-4",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "text-destructive font-medium",
                                    children: error
                                }, void 0, false, {
                                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                    lineNumber: 82,
                                    columnNumber: 17
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Button"], {
                                    asChild: true,
                                    variant: "outline",
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                        href: "/dashboard/voice-agent/control-center",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"], {
                                                className: "mr-2 h-4 w-4"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                                lineNumber: 85,
                                                columnNumber: 21
                                            }, this),
                                            "Configure Assistant"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                        lineNumber: 84,
                                        columnNumber: 19
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                    lineNumber: 83,
                                    columnNumber: 17
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                            lineNumber: 81,
                            columnNumber: 15
                        }, this) : assistantId ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex flex-col items-center gap-4 w-full",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$vapi$2f$CallButton$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CallButton"], {
                                    assistantId: assistantId,
                                    className: "w-full h-14 text-lg"
                                }, void 0, false, {
                                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                    lineNumber: 92,
                                    columnNumber: 17
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: "text-sm text-muted-foreground text-center",
                                    children: "Click to start a conversation. The AI will respond as configured."
                                }, void 0, false, {
                                    fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                    lineNumber: 96,
                                    columnNumber: 17
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                            lineNumber: 91,
                            columnNumber: 15
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$components$2f$ui$2f$button$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Button"], {
                            asChild: true,
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend_next$2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/dashboard/voice-agent/control-center",
                                children: "Configure Assistant First"
                            }, void 0, false, {
                                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                                lineNumber: 102,
                                columnNumber: 17
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                            lineNumber: 101,
                            columnNumber: 15
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                        lineNumber: 79,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
                lineNumber: 67,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
            lineNumber: 66,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/frontend_next/app/dashboard/voice-agent/test/page.tsx",
        lineNumber: 65,
        columnNumber: 5
    }, this);
}
}),
];

//# sourceMappingURL=frontend_next_b7efd040._.js.map