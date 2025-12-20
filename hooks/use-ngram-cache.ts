'use client';

import { useCallback, useRef } from 'react';
import type { NgramStats } from '@/types/ngram';

const STORAGE_KEY = 'typy-ngrams';

// Default configuration for n-gram fetching
export const NGRAM_CONFIG = {
    MIN_COUNT: 10,      // Minimum occurrences for an n-gram to be included
    GAMES_LIMIT: 100,   // Number of recent games to analyze
} as const;

export interface CachedNgrams {
    bigrams: NgramStats[];
    trigrams: NgramStats[];
    quadgrams: NgramStats[];
    gamesAnalyzed: number;
    fetchedAt: number;
}

export interface NgramCacheOptions {
    minCount?: number;
    gamesLimit?: number;
}

export function useNgramCache(visitorId: string | null, options?: NgramCacheOptions) {
    const isFetchingRef = useRef(false);
    
    const minCount = options?.minCount ?? NGRAM_CONFIG.MIN_COUNT;
    const gamesLimit = options?.gamesLimit ?? NGRAM_CONFIG.GAMES_LIMIT;

    // Read from localStorage
    const getCached = useCallback((): CachedNgrams | null => {
        if (typeof window === 'undefined') return null;
        const stored = localStorage.getItem(STORAGE_KEY);
        if (!stored) return null;
        try {
            return JSON.parse(stored);
        } catch {
            return null;
        }
    }, []);

    // Fire-and-forget background fetch
    const refreshInBackground = useCallback(() => {
        if (!visitorId) return;
        
        // Prevent multiple simultaneous fetches
        if (isFetchingRef.current) return;
        isFetchingRef.current = true;

        // Build URL with query parameters
        const params = new URLSearchParams({
            visitorId,
            minCount: String(minCount),
            gamesLimit: String(gamesLimit),
        });

        // Don't await - let it run in background
        fetch(`/api/stats/ngrams?${params}`)
            .then(res => res.json())
            .then(data => {
                if (data.trigrams && data.quadgrams) {
                    const cached: CachedNgrams = {
                        bigrams: data.bigrams || [],
                        trigrams: data.trigrams,
                        quadgrams: data.quadgrams,
                        gamesAnalyzed: data.gamesAnalyzed || 0,
                        fetchedAt: Date.now(),
                    };
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(cached));
                }
            })
            .catch(err => {
                console.error('Background n-gram fetch failed:', err);
                // That's fine, we'll use stale data
            })
            .finally(() => {
                isFetchingRef.current = false;
            });
    }, [visitorId, minCount, gamesLimit]);

    // Clear cache (useful for testing or user logout)
    const clearCache = useCallback(() => {
        if (typeof window === 'undefined') return;
        localStorage.removeItem(STORAGE_KEY);
    }, []);

    return { getCached, refreshInBackground, clearCache };
}
