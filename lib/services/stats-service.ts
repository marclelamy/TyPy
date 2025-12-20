import { db } from '@/lib/db';
import { games, keystrokes } from '@/lib/db/schema';
import { eq, desc, asc, sql } from 'drizzle-orm';

export async function getRecentGames(visitorId: string, limit: number = 10) {
    return await db
        .select()
        .from(games)
        .where(eq(games.visitorId, visitorId))
        .orderBy(desc(games.createdAt))
        .limit(limit);
}

export async function getGameById(gameId: string) {
    const game = await db.query.games.findFirst({
        where: eq(games.id, gameId),
    });
    
    if (!game) return null;
    
    const keystrokesData = await db
        .select()
        .from(keystrokes)
        .where(eq(keystrokes.gameId, gameId))
        .orderBy(keystrokes.timestamp);
    
    return {
        ...game,
        keystrokes: keystrokesData,
    };
}

export async function getAggregateStats(visitorId: string) {
    const result = await db
        .select({
            avgWpm: sql<number | null>`COALESCE(AVG(${games.wpm}), 0)`,
            avgAccuracy: sql<number | null>`COALESCE(AVG(${games.accuracy}), 0)`,
            totalGames: sql<number>`COUNT(*)`,
        })
        .from(games)
        .where(eq(games.visitorId, visitorId));
    
    const stats = result[0];
    return {
        avgWpm: stats?.avgWpm ?? 0,
        avgAccuracy: stats?.avgAccuracy ?? 0,
        totalGames: Number(stats?.totalGames) ?? 0,
    };
}

/**
 * Calculates the WPM improvement rate per hour of practice using linear regression.
 * Returns the slope of the regression line (WPM gained per hour played).
 */
export async function getWpmImprovementRate(visitorId: string) {
    // Fetch all games with WPM and duration, ordered by creation time
    const allGames = await db
        .select({
            wpm: games.wpm,
            duration: games.duration,
        })
        .from(games)
        .where(eq(games.visitorId, visitorId))
        .orderBy(asc(games.createdAt));
    
    // Filter out games without WPM or duration
    const validGames = allGames.filter(g => g.wpm !== null && g.duration !== null);
    
    if (validGames.length < 2) {
        return {
            wpmPerHour: null,
            totalHoursPlayed: 0,
            dataPoints: validGames.length,
        };
    }
    
    // Calculate cumulative hours for each game
    let cumulativeHours = 0;
    const dataPoints: { hours: number; wpm: number }[] = [];
    
    for (const game of validGames) {
        // Add duration in hours (duration is in milliseconds)
        cumulativeHours += (game.duration ?? 0) / 3_600_000;
        dataPoints.push({
            hours: cumulativeHours,
            wpm: game.wpm!,
        });
    }
    
    // Perform linear regression: y = mx + b where m is the slope (WPM per hour)
    // Using least squares method
    const n = dataPoints.length;
    let sumX = 0;
    let sumY = 0;
    let sumXY = 0;
    let sumX2 = 0;
    
    for (const point of dataPoints) {
        sumX += point.hours;
        sumY += point.wpm;
        sumXY += point.hours * point.wpm;
        sumX2 += point.hours * point.hours;
    }
    
    const denominator = n * sumX2 - sumX * sumX;
    
    // Avoid division by zero (would happen if all x values are the same)
    if (denominator === 0) {
        return {
            wpmPerHour: null,
            totalHoursPlayed: cumulativeHours,
            dataPoints: n,
        };
    }
    
    const slope = (n * sumXY - sumX * sumY) / denominator;
    
    return {
        wpmPerHour: slope,
        totalHoursPlayed: cumulativeHours,
        dataPoints: n,
    };
}
