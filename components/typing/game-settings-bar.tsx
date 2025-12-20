'use client';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import type { GameConfig } from '@/types/game';

interface GameSettingsBarProps {
    config: GameConfig;
    onConfigChange: (config: GameConfig) => void;
    loading?: boolean;
    ngramFetchedAt?: number;
}

function formatTimeAgo(timestamp: number): string {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

export function GameSettingsBar({ config, onConfigChange, loading, ngramFetchedAt }: GameSettingsBarProps) {
    const router = useRouter();
    const wordCounts = [10, 25, 50, 100];
    const difficulties: Array<'easy' | 'medium' | 'hard'> = ['easy', 'medium', 'hard'];
    const generationModes: Array<'paragraph' | 'vocabulary' | 'random'> = ['paragraph', 'vocabulary', 'random'];
    
    return (
        <div className="w-full border-b border-border bg-background/50 backdrop-blur-sm">
            <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground uppercase tracking-wider">Mode:</span>
                        <div className="flex gap-1">
                            {difficulties.map((diff) => (
                                <button
                                    key={diff}
                                    onClick={() => onConfigChange({ ...config, difficulty: diff })}
                                    className={cn(
                                        'px-3 py-1 text-sm rounded transition-colors',
                                        config.difficulty === diff
                                            ? 'bg-primary/20 text-primary'
                                            : 'text-muted-foreground hover:text-foreground'
                                    )}
                                >
                                    {diff.charAt(0).toUpperCase() + diff.slice(1)}
                                </button>
                            ))}
                        </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground uppercase tracking-wider">Words:</span>
                        <div className="flex gap-1">
                            {wordCounts.map((count) => (
                                <button
                                    key={count}
                                    onClick={() => onConfigChange({ ...config, wordCount: count })}
                                    className={cn(
                                        'px-3 py-1 text-sm rounded transition-colors',
                                        config.wordCount === count
                                            ? 'bg-primary/20 text-primary'
                                            : 'text-muted-foreground hover:text-foreground'
                                    )}
                                >
                                    {count}
                                </button>
                            ))}
                        </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground uppercase tracking-wider">Text:</span>
                        <div className="flex gap-1">
                            {generationModes.map((mode) => (
                                <button
                                    key={mode}
                                    onClick={() => onConfigChange({ ...config, generationMode: mode })}
                                    className={cn(
                                        'px-3 py-1 text-sm rounded transition-colors',
                                        (config.generationMode || 'paragraph') === mode
                                            ? 'bg-primary/20 text-primary'
                                            : 'text-muted-foreground hover:text-foreground'
                                    )}
                                >
                                    {mode === 'paragraph' ? 'Paragraph' : mode === 'vocabulary' ? 'Vocabulary' : 'Random'}
                                </button>
                            ))}
                        </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => onConfigChange({ ...config, learnFromMistakes: !config.learnFromMistakes })}
                            className={cn(
                                'px-3 py-1 text-sm rounded transition-colors',
                                config.learnFromMistakes
                                    ? 'bg-primary/20 text-primary'
                                    : 'text-muted-foreground hover:text-foreground'
                            )}
                            title="Practice words containing n-grams you struggle with"
                        >
                            <span className="text-xs uppercase tracking-wider">Learn</span>
                        </button>
                    </div>
                </div>
                
                <div className="flex items-center gap-4">
                    {ngramFetchedAt && (
                        <div className="text-xs text-muted-foreground" title={new Date(ngramFetchedAt).toLocaleString()}>
                            N-grams: {formatTimeAgo(ngramFetchedAt)}
                        </div>
                    )}
                    {loading && (
                        <div className="text-sm text-muted-foreground">
                            Loading...
                        </div>
                    )}
                </div>
                <Button onClick={() => router.push('/stats/ngrams')}>Stats</Button>
            </div>
        </div>
    );
}
