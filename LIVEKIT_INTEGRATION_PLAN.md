# LiveKit Official Template Integration Plan

## Current vs Template Comparison

### What You Have (Custom Implementation)
- ❌ Old LiveKit Components API
- ❌ Basic voice interface
- ❌ Manual token generation in backend
- ❌ Simple UI without proper state management
- ✅ Multi-tenant support
- ✅ Backend API integration
- ✅ Database-driven configuration

### What Template Provides (Official Best Practices)
- ✅ Latest LiveKit Components (@livekit/components-react)
- ✅ Modern session management with `SessionProvider`
- ✅ Proper audio rendering (`RoomAudioRenderer`)
- ✅ Better UI components (transcript, tiles, controls)
- ✅ Debug mode and error handling hooks
- ✅ Toaster notifications
- ✅ Theme support
- ✅ Better agent state visualization

## Integration Strategy

### Phase 1: Update Core Voice Component
**File**: `frontend_next/components/voice-agent/voice-app.tsx`

**Changes**:
1. Replace `LiveKitRoom` with `SessionProvider` + `useSession`
2. Add proper `AppSetup` component for hooks
3. Integrate `ViewController` for better state management
4. Add `Toaster` for notifications
5. Keep multi-tenant token generation

### Phase 2: Add Missing Components
**New Files**:
- `components/voice-agent/session-view.tsx` - Main view during session
- `components/voice-agent/welcome-view.tsx` - Initial view
- `components/voice-agent/chat-transcript.tsx` - Conversation history
- `components/voice-agent/view-controller.tsx` - State orchestration
- `hooks/useAgentErrors.ts` - Error handling
- `hooks/useDebug.ts` - Debug mode

### Phase 3: Update Token API
**File**: `frontend_next/app/api/voice-agent/connection-details/route.ts`

**Changes**:
1. Match template's endpoint structure
2. Keep multi-tenant authentication
3. Add room metadata for tenant_id
4. Use proper AccessToken from livekit-server-sdk

### Phase 4: Configuration
**File**: `frontend_next/app/dashboard/voice-agent/chat/page.tsx`

**Changes**:
1. Create AppConfig object
2. Pass tenant-specific settings
3. Use new App component

## Files to Create/Update

### Create New:
1. ✅ `components/voice-agent/session-view.tsx`
2. ✅ `components/voice-agent/welcome-view.tsx`
3. ✅ `components/voice-agent/chat-transcript.tsx`
4. ✅ `components/voice-agent/view-controller.tsx`
5. ✅ `components/voice-agent/tile-layout.tsx`
6. ✅ `components/livekit/toaster.tsx`
7. ✅ `components/livekit/alert-toast.tsx`
8. ✅ `hooks/useAgentErrors.ts`
9. ✅ `hooks/useDebug.ts`
10. ✅ `lib/livekit-utils.ts`

### Update Existing:
1. 🔄 `components/voice-agent/voice-app.tsx` - Replace with modern API
2. 🔄 `app/dashboard/voice-agent/chat/page.tsx` - Use new components
3. 🔄 Backend token generation - Add metadata properly

### Keep As-Is:
1. ✅ Multi-tenant authentication
2. ✅ Database configuration
3. ✅ API key management
4. ✅ Business logic in backend

## Key Improvements

1. **Better State Management**
   - SessionProvider handles connection lifecycle
   - useSession hook for reactive updates
   - Proper cleanup on disconnect

2. **Enhanced UI**
   - Chat transcript with auto-scroll
   - Agent status visualization
   - Better loading states
   - Toast notifications

3. **Error Handling**
   - useAgentErrors hook for debugging
   - Better error messages
   - Automatic reconnection

4. **Performance**
   - Lazy loading of components
   - Optimized re-renders
   - Better audio handling

5. **Developer Experience**
   - Debug mode toggle
   - Better TypeScript types
   - Hooks for common patterns

## Migration Steps

1. Install latest dependencies
2. Create new component structure
3. Update voice-app.tsx gradually
4. Test with existing backend
5. Remove old code
6. Document changes

## Tenant Configuration (No Change)

Tenants still control:
- API keys (Groq, Cartesia, Deepgram)
- Agent settings (prompt, voice, model)
- Business config

Platform still controls:
- LiveKit infrastructure
- Frontend framework
- Component library
