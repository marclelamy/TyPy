import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { games, keystrokes } from '@/lib/db/schema';
import { eq, desc, inArray } from 'drizzle-orm';
import { extractNgramsFromGame, calculateNgramStats } from '@/lib/services/ngram-service';
import type { NgramCalculation } from '@/types/ngram';
import type { Keystroke } from '@/types/game';

// Default values (can be overridden via query params)
const DEFAULT_MIN_COUNT = 1;
const DEFAULT_GAMES_LIMIT = 100;


export async function GET(request: NextRequest) {
    try {
        const visitorId = request.nextUrl.searchParams.get('visitorId');
        const minCountParam = request.nextUrl.searchParams.get('minCount');
        const gamesLimitParam = request.nextUrl.searchParams.get('gamesLimit');
        
        // Parse params with defaults
        const minCount = minCountParam ? parseInt(minCountParam, 10) : DEFAULT_MIN_COUNT;
        const gamesLimit = gamesLimitParam ? parseInt(gamesLimitParam, 10) : DEFAULT_GAMES_LIMIT;
        
        if (!visitorId) {
            return NextResponse.json(
                { error: 'Visitor ID is required' },
                { status: 400 }
            );
        }
        
        // Get recent games
        const recentGames = await db
            .select()
            .from(games)
            .where(eq(games.visitorId, visitorId))
            .orderBy(desc(games.createdAt))
            .limit(gamesLimit);
        
        if (recentGames.length === 0) {
            return NextResponse.json({ 
                bigrams: [],
                trigrams: [],
                quadgrams: [],
                gamesAnalyzed: 0 
            });
        }
        
        const gameIds = recentGames.map(g => g.id);
        
        // Fetch ALL keystrokes for these games in ONE query
        const allKeystrokesData = await db
            .select()
            .from(keystrokes)
            .where(inArray(keystrokes.gameId, gameIds))
            .orderBy(keystrokes.gameId, keystrokes.timestamp);
        
        // Group keystrokes by game_id
        const keystrokesByGame = new Map<string, Keystroke[]>();
        for (const ks of allKeystrokesData) {
            if (!keystrokesByGame.has(ks.gameId)) {
                keystrokesByGame.set(ks.gameId, []);
            }
            keystrokesByGame.get(ks.gameId)!.push({
                key: ks.key,
                expectedKey: ks.expectedKey,
                isCorrect: ks.isCorrect === 1,
                timestamp: Number(ks.timestamp),
                shiftPressed: ks.shiftPressed as 'left' | 'right' | null,
            });
        }
        
        // Calculate all three n-gram types at once
        const bigramCalculations: NgramCalculation[] = [];
        const trigramCalculations: NgramCalculation[] = [];
        const quadgramCalculations: NgramCalculation[] = [];
        
        for (const game of recentGames) {
            const gameKeystrokes = keystrokesByGame.get(game.id) || [];
            
            // Extract all three n-gram types for this game
            bigramCalculations.push(...extractNgramsFromGame(game.sentence, gameKeystrokes, 2));
            trigramCalculations.push(...extractNgramsFromGame(game.sentence, gameKeystrokes, 3));
            quadgramCalculations.push(...extractNgramsFromGame(game.sentence, gameKeystrokes, 4));
        }
        
        // Calculate aggregate stats for all three types
        const bigramStats = calculateNgramStats(bigramCalculations)
            .filter(stat => stat.count >= minCount)
            .filter(stat => !stat.ngram.includes(' '))
            .sort((a, b) => b.medianTime - a.medianTime);
            
        const trigramStats = calculateNgramStats(trigramCalculations)
            .filter(stat => stat.count >= minCount)
            .filter(stat => !stat.ngram.includes(' '))
            .sort((a, b) => b.medianTime - a.medianTime);
            
        const quadgramStats = calculateNgramStats(quadgramCalculations)
            .filter(stat => stat.count >= minCount)
            .filter(stat => !stat.ngram.includes(' '))
            .sort((a, b) => b.medianTime - a.medianTime);

        return NextResponse.json(
            { 
                bigrams: bigramStats,
                trigrams: trigramStats,
                quadgrams: quadgramStats,
                gamesAnalyzed: recentGames.length 
            },
            {
                headers: {
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                }
            }
        );
    } catch (error) {
        console.error('Error fetching n-gram stats:', error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Failed to fetch n-gram stats' },
            { status: 500 }
        );
    }
}
