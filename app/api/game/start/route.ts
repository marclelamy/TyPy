import { NextRequest, NextResponse } from 'next/server';
import { generateSentence, generateSentenceWithLLM, generateVocabularySentence } from '@/lib/services/sentence-service';
import { createGame } from '@/lib/services/game-service';
import type { GameConfig } from '@/types/game';
import type { NgramStats } from '@/types/ngram';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const config: GameConfig = {
            difficulty: body.difficulty || 'medium',
            wordCount: body.wordCount || 25,
            wordLengthMin: body.wordLengthMin || 3,
            wordLengthMax: body.wordLengthMax || 10,
            generationMode: body.generationMode || 'paragraph', // Default 'paragraph'
            learnFromMistakes: body.learnFromMistakes || false,
        };
        
        const visitorId = body.visitorId;
        if (!visitorId) {
            return NextResponse.json({ error: 'visitorId is required' }, { status: 400 });
        }
        
        // Get n-gram stats if learning from mistakes is enabled
        const ngramStats: NgramStats[] | undefined = config.learnFromMistakes && body.ngramStats
            ? [...(body.ngramStats.trigrams || []), ...(body.ngramStats.quadgrams || [])]
            : undefined;
        
        // Generate sentence based on generation mode
        let sentence: string;
        if (config.generationMode === 'vocabulary') {
            sentence = await generateVocabularySentence();
        } else if (config.generationMode === 'paragraph' || config.generationMode === undefined) {
            try {
                sentence = await generateSentenceWithLLM(config, ngramStats);
            } catch (error) {
                console.error('LLM generation failed, falling back to simple generation:', error);
                sentence = await generateSentence(config, ngramStats);
            }
        } else {
            sentence = await generateSentence(config, ngramStats);
        }
        
        const gameId = await createGame(visitorId, sentence, config);
        
        return NextResponse.json({ gameId, sentence });
    } catch (error) {
        console.error('Error starting game:', error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : 'Failed to start game' },
            { status: 500 }
        );
    }
}
