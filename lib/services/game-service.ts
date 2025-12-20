import { db } from '@/lib/db';
import { games, keystrokes } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';
import type { Keystroke, GameConfig } from '@/types/game';

export async function createGame(
    visitorId: string,
    sentence: string,
    config: GameConfig
) {
    const gameId = `game-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    await db.insert(games).values({
        id: gameId,
        visitorId,
        sentence,
        // Note: config column not in DB yet - needs migration
    });
    
    return gameId;
}

export async function saveKeystrokes(gameId: string, keystrokesData: Keystroke[], visitorId?: string) {
    if (keystrokesData.length === 0) return;
    
    await db.insert(keystrokes).values(
        keystrokesData.map(ks => ({
            gameId,
            visitorId,
            key: ks.key,
            expectedKey: ks.expectedKey,
            isCorrect: ks.isCorrect ? 1 : 0,
            shiftPressed: ks.shiftPressed || null,
            timestamp: ks.timestamp, // bigint with mode: 'number' expects a number, not BigInt
        }))
    );
}

export async function completeGame(
    gameId: string,
    stats: {
        wpm: number;
        accuracy: number;
        duration: number;
        correctCount: number;
        errorCount: number;
    }
) {
    await db
        .update(games)
        .set({
            wpm: stats.wpm,
            accuracy: stats.accuracy,
            duration: stats.duration,
            correctCount: stats.correctCount,
            errorCount: stats.errorCount,
        })
        .where(eq(games.id, gameId));
}
