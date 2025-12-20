import { checkOrCreateUserIdentifiers } from '@/lib/guest-user-uuid';

export async function getOrCreateVisitorId(): Promise<string> {
    if (typeof window === 'undefined') {
        // Server-side: generate a temporary ID (shouldn't happen in practice)
        return `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    const identifiers = await checkOrCreateUserIdentifiers();
    // Prefer localStorage, fallback to cookie, then sessionStorage
    return identifiers.localStorage || identifiers.cookie || identifiers.sessionStorage || identifiers.indexedDB || identifiers.fingerprint;
}
