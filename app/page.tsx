'use client';

import { useEffect, useState, useRef } from 'react';
import { useGameState } from '@/hooks/use-game-state';
import { useVisitorId } from '@/hooks/use-visitor-id';
import { useNgramCache } from '@/hooks/use-ngram-cache';
import { GameSettingsBar } from '@/components/typing/game-settings-bar';
import { TypingArea } from '@/components/typing/typing-area';
import { WpmDisplay } from '@/components/typing/wpm-display';
import { Results } from '@/components/typing/results';
import { calcChartData, calcWpm, calcAccuracy } from '@/lib/utils/scoring';
import type { GameConfig as GameConfigType, GameResult } from '@/types/game';

export default function Home() {
    const { visitorId, loading: visitorLoading } = useVisitorId();
    const gameState = useGameState();
    const { getCached, refreshInBackground } = useNgramCache(visitorId);
    const [config, setConfig] = useState<GameConfigType>({
        difficulty: 'medium',
        wordCount: 25,
        wordLengthMin: 3,
        wordLengthMax: 10,
        generationMode: 'paragraph',
        learnFromMistakes: true,
    });
    const configRef = useRef(config);
    configRef.current = config;

    // Load sentence when visitorId available and status is idle
    useEffect(() => {
        if (!visitorId || visitorLoading) return;
        if (gameState.status === 'idle') {
            // Get cached n-grams if learning from mistakes is enabled
            const cachedNgrams = configRef.current.learnFromMistakes ? getCached() : null;
            gameState.loadSentence(configRef.current, visitorId, cachedNgrams);
            // Trigger background refresh to update n-grams for next game
            refreshInBackground();
        }
    }, [visitorId, visitorLoading, gameState.status, gameState.loadSentence, getCached, refreshInBackground]);

    // Reload sentence when config changes (only when ready, not while playing)
    useEffect(() => {
        if (!visitorId || visitorLoading) return;
        if (gameState.status === 'ready') {
            // Get cached n-grams if learning from mistakes is enabled
            const cachedNgrams = config.learnFromMistakes ? getCached() : null;
            gameState.loadSentence(config, visitorId, cachedNgrams);
            // Trigger background refresh to update n-grams for next game
            refreshInBackground();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [config.difficulty, config.wordCount, config.wordLengthMin, config.wordLengthMax, config.generationMode, config.learnFromMistakes]);

    useEffect(() => {
        if (gameState.status === 'finished' && visitorId && gameState.gameId) {
            gameState.submitGame(visitorId);
        }
    }, [gameState.status, visitorId, gameState.gameId, gameState.submitGame]);

    const handlePlayAgain = () => {
        gameState.reset();
    };

    if (visitorLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
                <div>Loading...</div>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen flex-col bg-background text-foreground">
            {/* Settings bar at top - always visible */}
            <GameSettingsBar
                config={config}
                onConfigChange={setConfig}
                loading={gameState.status === 'loading'}
                ngramFetchedAt={getCached()?.fetchedAt}
            />

            <div className="flex-1 flex flex-col items-center justify-center w-full max-w-6xl mx-auto px-4 py-8">
                {(gameState.status === 'loading' || gameState.status === 'idle') && (
                    <div className="text-center text-muted-foreground">Loading...</div>
                )}

                {(gameState.status === 'ready' || gameState.status === 'playing') && gameState.sentence && (
                    <div className="w-full space-y-12">
                        {gameState.status === 'playing' && (
                            <WpmDisplay wpm={gameState.realTimeWpm} accuracy={gameState.accuracy} />
                        )}
                        <TypingArea
                            sentence={gameState.sentence}
                            currentIndex={gameState.currentIndex}
                            typedChars={gameState.typedChars}
                        />
                    </div>
                )}

                {gameState.status === 'finished' && (
                    <div className="w-full">
                        {(() => {
                            const duration = gameState.keystrokes.length > 0
                                ? gameState.keystrokes[gameState.keystrokes.length - 1].timestamp -
                                (gameState.keystrokes[0].timestamp)
                                : 0;
                            const correctCount = gameState.keystrokes.filter(k => k.isCorrect).length;
                            const errorCount = gameState.keystrokes.length - correctCount;
                            const chartData = calcChartData(gameState.keystrokes, gameState.sentence);
                            
                            // Calculate WPM and accuracy directly from keystrokes
                            // (realTimeWpm returns 0 when status is 'finished')
                            const wpm = calcWpm(correctCount, duration);
                            const accuracy = calcAccuracy(correctCount, gameState.keystrokes.length);

                            const result: GameResult = {
                                wpm,
                                accuracy,
                                duration,
                                correctCount,
                                errorCount,
                                chartData,
                            };

                            return (
                                <Results
                                    result={result}
                                    onPlayAgain={handlePlayAgain}
                                />
                            );
                        })()}
                    </div>
                )}
            </div>
        </div>
    );
}
