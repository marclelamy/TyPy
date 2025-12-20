import { NextRequest, NextResponse } from 'next/server';
import { saveKeystrokes, completeGame } from '@/lib/services/game-service';
import type { Keystroke } from '@/types/game';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { gameId, keystrokes: keystrokesData, finalStats, visitorId } = body;
        
        if (!gameId) {
            return NextResponse.json({ error: 'gameId is required' }, { status: 400 });
        }
        
        if (keystrokesData && Array.isArray(keystrokesData)) {
            await saveKeystrokes(gameId, keystrokesData as Keystroke[], visitorId);
        }
        
        if (finalStats) {
            await completeGame(gameId, finalStats);
        }
        
        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('Error submitting game:', error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Failed to submit game' },
            { status: 500 }
        );
    }
}
