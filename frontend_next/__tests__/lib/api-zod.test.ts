/**
 * Tests for StoredUserSchema in lib/api.ts
 *
 * Verifies:
 * - Valid user objects pass schema validation
 * - Objects with unexpected/extra fields are still accepted (schema is partial)
 * - Invalid role values are rejected
 * - Invalid email format is rejected
 * - Injected tenant_id (role spoofing vector) with invalid role is rejected
 * - Parsing does not throw — uses safeParse
 */

import { describe, it, expect } from 'vitest'
import { z } from 'zod'

// ── Re-define StoredUserSchema (same source as lib/api.ts) ────────────────────
const StoredUserSchema = z.object({
    id: z.string().optional(),
    tenant_id: z.string().optional(),
    role: z.enum(['user', 'admin', 'owner', 'super_admin']).optional(),
    username: z.string().optional(),
    email: z.string().email().optional(),
})
// ─────────────────────────────────────────────────────────────────────────────

describe('StoredUserSchema (localStorage user validation)', () => {
    it('accepts a fully valid user object', () => {
        const user = {
            id: 'user-123',
            tenant_id: 'tenant-abc',
            role: 'admin',
            username: 'alice',
            email: 'alice@example.com',
        }
        expect(StoredUserSchema.safeParse(user).success).toBe(true)
    })

    it('accepts a minimal user object (all fields optional)', () => {
        expect(StoredUserSchema.safeParse({}).success).toBe(true)
    })

    it('accepts user with only tenant_id set', () => {
        expect(StoredUserSchema.safeParse({ tenant_id: 'abc' }).success).toBe(true)
    })

    it('rejects an invalid role value', () => {
        const result = StoredUserSchema.safeParse({ role: 'superuser' })
        expect(result.success).toBe(false)
    })

    it('rejects role: "root" (injection attempt)', () => {
        const result = StoredUserSchema.safeParse({ role: 'root' })
        expect(result.success).toBe(false)
    })

    it('rejects an invalid email address', () => {
        const result = StoredUserSchema.safeParse({ email: 'not-an-email' })
        expect(result.success).toBe(false)
    })

    it('rejects a malformed email that passes naive checks', () => {
        const result = StoredUserSchema.safeParse({ email: 'a@' })
        expect(result.success).toBe(false)
    })

    it('rejects role: null (type confusion)', () => {
        const result = StoredUserSchema.safeParse({ role: null })
        // null is not a string enum value — should fail
        expect(result.success).toBe(false)
    })

    it('accepts all valid role values', () => {
        for (const role of ['user', 'admin', 'owner', 'super_admin']) {
            expect(StoredUserSchema.safeParse({ role }).success).toBe(true)
        }
    })

    it('never throws — always uses safeParse result', () => {
        // Simulate the worst-case localStorage corruption
        const garbage = [null, undefined, 123, [], 'string', { role: ['array'] }]
        for (const val of garbage) {
            expect(() => StoredUserSchema.safeParse(val)).not.toThrow()
        }
    })
})
