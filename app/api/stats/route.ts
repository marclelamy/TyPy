import { NextRequest, NextResponse } from 'next/server';
import { getRecentGames, getGameById, getAggregateStats, getWpmImprovementRate } from '@/lib/services/stats-service';

export async function GET(request: NextRequest) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const visitorId = searchParams.get('visitorId');
        const gameId = searchParams.get('gameId');
        
        if (!visitorId) {
            return NextResponse.json({ error: 'visitorId is required' }, { status: 400 });
        }
        
        if (gameId) {
            const game = await getGameById(gameId);
            if (!game) {
                return NextResponse.json({ error: 'Game not found' }, { status: 404 });
            }
            return NextResponse.json({ game });
        }
        
        const limit = parseInt(searchParams.get('limit') || '10');
        const [recentGames, aggregateStats, improvementRate] = await Promise.all([
            getRecentGames(visitorId, limit),
            getAggregateStats(visitorId),
            getWpmImprovementRate(visitorId),
        ]);
        
        return NextResponse.json({
            recentGames,
            aggregateStats,
            improvementRate,
        });
    } catch (error) {
        console.error('Error fetching stats:', error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Failed to fetch stats' },
            { status: 500 }
        );
    }
}
