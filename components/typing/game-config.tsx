'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import type { GameConfig } from '@/types/game';

interface GameConfigProps {
    onStart: (config: GameConfig) => void;
    loading?: boolean;
}

const STORAGE_KEY = 'typy-game-config';

export function GameConfig({ onStart, loading }: GameConfigProps) {
    const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
    const [wordCount, setWordCount] = useState(25);
    const [wordLengthMin, setWordLengthMin] = useState(3);
    const [wordLengthMax, setWordLengthMax] = useState(10);
    const [learnFromMistakes, setLearnFromMistakes] = useState(true);
    const [generationMode, setGenerationMode] = useState<'paragraph' | 'vocabulary' | 'random'>('paragraph');
    
    // Load saved config from localStorage on mount
    useEffect(() => {
        const savedConfig = localStorage.getItem(STORAGE_KEY);
        if (savedConfig) {
            try {
                const config = JSON.parse(savedConfig);
                if (config.difficulty) setDifficulty(config.difficulty);
                if (config.wordCount !== undefined) setWordCount(config.wordCount);
                if (config.wordLengthMin !== undefined) setWordLengthMin(config.wordLengthMin);
                if (config.wordLengthMax !== undefined) setWordLengthMax(config.wordLengthMax);
                if (config.learnFromMistakes !== undefined) setLearnFromMistakes(config.learnFromMistakes);
                if (config.generationMode) setGenerationMode(config.generationMode);
            } catch (e) {
                // Invalid JSON, ignore and use defaults
                console.warn('Failed to load saved game config:', e);
            }
        }
    }, []);
    
    const handleStart = () => {
        const config: GameConfig = {
            difficulty,
            wordCount,
            wordLengthMin,
            wordLengthMax,
            generationMode,
            learnFromMistakes,
        };
        
        // Save config to localStorage for next time
        localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
        
        onStart(config);
    };
    
    return (
        <Card className="w-full max-w-md mx-auto">
            <CardHeader>
                <CardTitle>Game Settings</CardTitle>
                <CardDescription>Configure your typing test</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium">Difficulty</label>
                    <Select value={difficulty} onValueChange={(v: string) => setDifficulty(v as 'easy' | 'medium' | 'hard')}>
                        <SelectTrigger>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="easy">Easy</SelectItem>
                            <SelectItem value="medium">Medium</SelectItem>
                            <SelectItem value="hard">Hard</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                
                <div className="space-y-2">
                    <label className="text-sm font-medium">Text Mode</label>
                    <Select value={generationMode} onValueChange={(v: string) => setGenerationMode(v as 'paragraph' | 'vocabulary' | 'random')}>
                        <SelectTrigger>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="paragraph">Paragraph (LLM)</SelectItem>
                            <SelectItem value="vocabulary">Vocabulary (LLM)</SelectItem>
                            <SelectItem value="random">Random Words</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                
                <div className="space-y-2">
                    <label className="text-sm font-medium">Word Count</label>
                    <Input
                        type="number"
                        value={wordCount}
                        onChange={(e) => setWordCount(parseInt(e.target.value) || 25)}
                        min={10}
                        max={100}
                    />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Min Length</label>
                        <Input
                            type="number"
                            value={wordLengthMin}
                            onChange={(e) => setWordLengthMin(parseInt(e.target.value) || 3)}
                            min={1}
                            max={20}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Max Length</label>
                        <Input
                            type="number"
                            value={wordLengthMax}
                            onChange={(e) => setWordLengthMax(parseInt(e.target.value) || 10)}
                            min={1}
                            max={20}
                        />
                    </div>
                </div>
                
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <label className="text-sm font-medium">Learn from Mistakes</label>
                        <p className="text-xs text-muted-foreground">
                            Practice words with your weak n-grams
                        </p>
                    </div>
                    <button
                        type="button"
                        role="switch"
                        aria-checked={learnFromMistakes}
                        onClick={() => setLearnFromMistakes(!learnFromMistakes)}
                        className={`
                            relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent 
                            transition-colors duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 
                            focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background
                            ${learnFromMistakes ? 'bg-primary' : 'bg-input'}
                        `}
                    >
                        <span
                            className={`
                                pointer-events-none inline-block h-5 w-5 transform rounded-full bg-background shadow-lg 
                                ring-0 transition duration-200 ease-in-out
                                ${learnFromMistakes ? 'translate-x-5' : 'translate-x-0'}
                            `}
                        />
                    </button>
                </div>
                
                <Button onClick={handleStart} disabled={loading} className="w-full">
                    {loading ? 'Starting...' : 'Start Game'}
                </Button>
            </CardContent>
        </Card>
    );
}
