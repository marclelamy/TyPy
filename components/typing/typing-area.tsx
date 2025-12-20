'use client';

import { cn } from '@/lib/utils';
import type { TypedChar } from '@/types/game';

interface TypingAreaProps {
    sentence: string;
    currentIndex: number;
    typedChars: Record<number, TypedChar>;
}

export function TypingArea({ sentence, currentIndex, typedChars }: TypingAreaProps) {
    return (
        <div className="w-full max-w-5xl mx-auto px-4">
            <div className="text-2xl md:text-3xl font-mono leading-relaxed break-words whitespace-normal text-center">
                {sentence.split('').map((char, index) => {
                    let className = 'text-muted-foreground';
                    
                    if (index < currentIndex) {
                        const typedChar = typedChars[index];
                        if (typedChar) {
                            // Use destructive color for incorrect, accent for correct
                            className = typedChar.isCorrect 
                                ? 'text-accent-foreground' 
                                : 'text-destructive bg-destructive/20';
                        }
                    } else if (index === currentIndex) {
                        className = 'text-primary bg-primary/20';
                    }
                    
                    return (
                        <span 
                            key={index} 
                            className={cn(className)}
                        >
                            {char === ' ' ? ' ' : char}
                        </span>
                    );
                })}
            </div>
        </div>
    );
}
