'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { ResultsChart } from './results-chart';
import type { GameResult } from '@/types/game';

interface ResultsProps {
    result: GameResult;
    onPlayAgain: () => void;
    onViewStats?: () => void;
}

export function Results({ result, onPlayAgain, onViewStats }: ResultsProps) {
    // Press Enter to play again
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                onPlayAgain();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [onPlayAgain]);

    return (
        <div className="w-full max-w-4xl mx-auto space-y-8">
            {/* Main stats row */}
            <div className="flex items-start gap-8">
                {/* Left side: Big WPM and Accuracy */}
                <div className="space-y-4">
                    <div>
                        <div className="text-sm text-muted-foreground">wpm</div>
                        <div className="text-6xl font-bold text-yellow-500">{Math.round(result.wpm)}</div>
                    </div>
                    <div>
                        <div className="text-sm text-muted-foreground">acc</div>
                        <div className="text-4xl font-bold text-yellow-500">{Math.round(result.accuracy)}%</div>
                    </div>
                </div>

                {/* Right side: Chart */}
                <div className="flex-1">
                    {result.chartData && result.chartData.length > 0 && (
                        <ResultsChart data={result.chartData} />
                    )}
                </div>
            </div>

            {/* Secondary stats row */}
            <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                    <div className="text-sm text-muted-foreground">test type</div>
                    <div className="text-yellow-500 font-medium">words</div>
                </div>
                <div>
                    <div className="text-sm text-muted-foreground">characters</div>
                    <div className="text-xl font-bold text-foreground">
                        {result.correctCount}/{result.errorCount}
                    </div>
                </div>
                <div>
                    <div className="text-sm text-muted-foreground">errors</div>
                    <div className="text-xl font-bold text-destructive">{result.errorCount}</div>
                </div>
                <div>
                    <div className="text-sm text-muted-foreground">time</div>
                    <div className="text-xl font-bold text-foreground">{Math.round(result.duration / 1000)}s</div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex justify-center gap-4">
                <Button onClick={onPlayAgain} size="lg">
                    Play Again
                </Button>
                {onViewStats && (
                    <Button onClick={onViewStats} variant="outline" size="lg">
                        View Stats
                    </Button>
                )}
            </div>
        </div>
    );
}
