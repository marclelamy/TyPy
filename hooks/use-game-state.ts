import { useState, useCallback, useRef } from 'react';
import { useKeyCapture, type KeyPress } from './use-key-capture';
import { calcWpm, calcAccuracy, calcDuration } from '@/lib/utils/scoring';
import type { GameState, Keystroke, GameConfig, GameResult } from '@/types/game';
import type { CachedNgrams } from './use-ngram-cache';

export function useGameState() {
    const [state, setState] = useState<GameState>({
        status: 'idle',
        gameId: null,
        sentence: '',
        currentIndex: 0,
        keystrokes: [],
        typedChars: {},
        startTime: null,
    });
    const isLoadingRef = useRef(false);
    
    const handleKeyPress = useCallback(
        (keyPress: KeyPress) => {
            if (state.status !== 'ready' && state.status !== 'playing') return;
            
            setState(prev => {
                // If we're in 'ready' status and this is the first keystroke, start timing
                const isFirstKeystroke = prev.status === 'ready' && prev.keystrokes.length === 0;
                const startTime = isFirstKeystroke ? keyPress.timestamp : prev.startTime;
                
                const expectedKey = prev.sentence[prev.currentIndex] || '';
                const isCorrect = keyPress.key === expectedKey;
                
                const keystroke: Keystroke = {
                    key: keyPress.key,
                    expectedKey,
                    isCorrect,
                    timestamp: keyPress.timestamp,
                    shiftPressed: keyPress.shiftPressed,
                };
                
                const newKeystrokes = [...prev.keystrokes, keystroke];
                let newIndex = prev.currentIndex;
                const newTypedChars = { ...prev.typedChars };
                
                if (keyPress.key === 'Backspace') {
                    // Go back one position, clear the typed char at current position
                    newIndex = Math.max(0, prev.currentIndex - 1);
                    delete newTypedChars[newIndex];
                } else if (keyPress.key !== 'Escape') {
                    // Record what was typed at this position (for display)
                    newTypedChars[prev.currentIndex] = {
                        key: keyPress.key,
                        expectedKey,
                        isCorrect,
                    };
                    newIndex = prev.currentIndex + 1;
                }
                
                const isFinished = newIndex >= prev.sentence.length;
                
                return {
                    ...prev,
                    status: isFirstKeystroke ? 'playing' : (isFinished ? 'finished' : 'playing'),
                    currentIndex: newIndex,
                    keystrokes: newKeystrokes,
                    typedChars: newTypedChars,
                    startTime,
                };
            });
        },
        [state.status]
    );
    
    useKeyCapture({
        enabled: state.status === 'ready' || state.status === 'playing',
        onKeyPress: handleKeyPress,
    });
    
    const loadSentence = useCallback(async (
        config: GameConfig, 
        visitorId: string,
        ngramStats?: CachedNgrams | null
    ) => {
        // Prevent multiple simultaneous loads
        if (isLoadingRef.current) return;
        isLoadingRef.current = true;
        
        setState(prev => ({ ...prev, status: 'loading' }));
        
        try {
            // Build request body, include n-gram stats if learning from mistakes
            const requestBody: Record<string, unknown> = { ...config, visitorId };
            if (config.learnFromMistakes && ngramStats) {
                requestBody.ngramStats = {
                    trigrams: ngramStats.trigrams,
                    quadgrams: ngramStats.quadgrams,
                };
            }
            
            const response = await fetch('/api/game/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });
            
            if (!response.ok) {
                throw new Error('Failed to load sentence');
            }
            
            const { gameId, sentence } = await response.json();
            
            setState({
                status: 'ready',
                gameId,
                sentence,
                currentIndex: 0,
                keystrokes: [],
                typedChars: {},
                startTime: null,
            });
        } catch (error) {
            console.error('Error loading sentence:', error);
            setState(prev => ({ ...prev, status: 'idle' }));
        } finally {
            isLoadingRef.current = false;
        }
    }, []);
    
    // Keep startGame for backwards compatibility, but it now just loads the sentence
    const startGame = loadSentence;
    
    const submitGame = useCallback(async (visitorId: string) => {
        if (!state.gameId || state.keystrokes.length === 0) return;
        
        const duration = calcDuration(state.keystrokes);
        const correctCount = state.keystrokes.filter(k => k.isCorrect).length;
        const errorCount = state.keystrokes.length - correctCount;
        const wpm = calcWpm(correctCount, duration);
        const accuracy = calcAccuracy(correctCount, state.keystrokes.length);
        
        const finalStats: GameResult = {
            wpm,
            accuracy,
            duration,
            correctCount,
            errorCount,
        };
        
        try {
            await fetch('/api/game/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gameId: state.gameId,
                    keystrokes: state.keystrokes,
                    finalStats,
                    visitorId,
                }),
            });
        } catch (error) {
            console.error('Error submitting game:', error);
        }
        
        return finalStats;
    }, [state]);
    
    const reset = useCallback(() => {
        setState({
            status: 'idle',
            gameId: null,
            sentence: '',
            currentIndex: 0,
            keystrokes: [],
            typedChars: {},
            startTime: null,
        });
    }, []);
    
    const realTimeWpm = state.status === 'playing' && state.keystrokes.length > 0
        ? calcWpm(
            state.keystrokes.filter(k => k.isCorrect).length,
            calcDuration(state.keystrokes)
        )
        : 0;
    
    const accuracy = state.keystrokes.length > 0
        ? calcAccuracy(
            state.keystrokes.filter(k => k.isCorrect).length,
            state.keystrokes.length
        )
        : 0;
    
    return {
        ...state,
        startGame,
        loadSentence,
        submitGame,
        reset,
        realTimeWpm,
        accuracy,
    };
}
