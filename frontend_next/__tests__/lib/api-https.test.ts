/**
 * Tests for HTTPS enforcement and withCredentials removal in lib/api.ts and lib/api/calls.ts
 *
 * Verifies:
 * - Neither file uses http:// for non-localhost environments
 * - Neither file sets withCredentials: true
 * - StoredUserSchema validates and strips bad localStorage data
 * - Logout handlers clear tenant_id and user keys
 */

import { describe, it, expect } from 'vitest'
import { readFileSync } from 'fs'
import { resolve } from 'path'

const ROOT = resolve(__dirname, '../..')

function readFile(relative: string): string {
    return readFileSync(resolve(ROOT, relative), 'utf-8')
}

describe('lib/api.ts HTTPS + credential security (H2, H7)', () => {
    const src = readFile('lib/api.ts')

    it('does not set withCredentials: true', () => {
        expect(src).not.toContain('withCredentials: true')
    })

    it('non-localhost fallback URL uses https://', () => {
        // The only http:// allowed is the localhost branch
        const lines = src.split('\n').filter(l =>
            l.includes('http://') && !l.includes('localhost') && !l.includes('127.0.0.1')
        )
        expect(lines.length).toBe(0)
    })

    it('imports zod for localStorage user validation', () => {
        expect(src).toMatch(/from ['"]zod['"]/)
    })

    it('uses safeParse (not JSON.parse directly) on localStorage user', () => {
        expect(src).toContain('.safeParse(')
    })

    it('removes bad user data from localStorage on schema failure', () => {
        expect(src).toContain("localStorage.removeItem('user')")
    })

    it('401 handler clears access_token from localStorage', () => {
        expect(src).toContain("localStorage.removeItem('access_token')")
    })

    it('401 handler clears tenant_id from localStorage', () => {
        expect(src).toContain("localStorage.removeItem('tenant_id')")
    })
})

describe('lib/api/calls.ts HTTPS + credential security (H2, H7)', () => {
    const src = readFile('lib/api/calls.ts')

    it('does not set withCredentials: true', () => {
        expect(src).not.toContain('withCredentials: true')
    })

    it('non-localhost fallback URL uses https://', () => {
        const lines = src.split('\n').filter(l =>
            l.includes('http://') && !l.includes('localhost') && !l.includes('127.0.0.1')
        )
        expect(lines.length).toBe(0)
    })
})

describe('Sidebar + MobileFootbar logout completeness', () => {
    const sidebar = readFile('components/dashboard/Sidebar.tsx')
    const footbar = readFile('components/dashboard/MobileFootbar.tsx')

    for (const [name, src] of [['Sidebar.tsx', sidebar], ['MobileFootbar.tsx', footbar]]) {
        it(`${name}: logout clears access_token`, () => {
            expect(src).toMatch(/removeItem\(["']access_token["']\)/)
        })

        it(`${name}: logout clears tenant_id`, () => {
            expect(src).toMatch(/removeItem\(["']tenant_id["']\)/)
        })

        it(`${name}: logout clears user object`, () => {
            expect(src).toMatch(/removeItem\(["']user["']\)/)
        })
    }
})
