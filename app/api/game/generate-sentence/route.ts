import { NextRequest, NextResponse } from 'next/server';
import { generateSentenceWithLLM } from '@/lib/services/sentence-service';
import type { GameConfig } from '@/types/game';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const config: GameConfig = {
            difficulty: body.difficulty || 'medium',
            wordCount: body.wordCount || 25,
            wordLengthMin: body.wordLengthMin || 3,
            wordLengthMax: body.wordLengthMax || 10,
        };
        
        const sentence = await generateSentenceWithLLM(config);
        
        return NextResponse.json({ sentence });
    } catch (error) {
        console.error('Error generating sentence with LLM:', error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Failed to generate sentence with LLM' },
            { status: 500 }
        );
    }
}
