import { useEffect, useCallback } from 'react';

export interface KeyPress {
    key: string;
    timestamp: number;
    shiftKey: boolean;
    shiftPressed?: 'left' | 'right';
}

interface UseKeyCaptureOptions {
    enabled: boolean;
    onKeyPress: (keyPress: KeyPress) => void;
}

export function useKeyCapture({ enabled, onKeyPress }: UseKeyCaptureOptions) {
    const handleKeyDown = useCallback(
        (event: KeyboardEvent) => {
            if (!enabled) return;
            
            // Ignore modifier keys alone
            if (['Shift', 'Control', 'Alt', 'Meta'].includes(event.key)) {
                return;
            }
            
            // Handle special keys
            if (event.key === 'Backspace' || event.key === 'Escape') {
                onKeyPress({
                    key: event.key,
                    timestamp: Date.now(),
                    shiftKey: event.shiftKey,
                    shiftPressed: event.shiftKey
                        ? event.location === KeyboardEvent.DOM_KEY_LOCATION_LEFT
                            ? 'left'
                            : 'right'
                        : undefined,
                });
                return;
            }
            
            // Ignore keys that don't produce characters
            if (event.key.length > 1 && !['Enter', 'Tab', 'Space'].includes(event.key)) {
                return;
            }
            
            onKeyPress({
                key: event.key,
                timestamp: Date.now(),
                shiftKey: event.shiftKey,
                shiftPressed: event.shiftKey
                    ? event.location === KeyboardEvent.DOM_KEY_LOCATION_LEFT
                        ? 'left'
                        : 'right'
                    : undefined,
            });
        },
        [enabled, onKeyPress]
    );
    
    useEffect(() => {
        if (!enabled) return;
        
        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [enabled, handleKeyDown]);
}
