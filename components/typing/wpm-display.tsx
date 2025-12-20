'use client';

interface WpmDisplayProps {
    wpm: number;
    accuracy: number;
}

export function WpmDisplay({ wpm, accuracy }: WpmDisplayProps) {
    return (
        <div className="flex gap-12 justify-center items-center">
            <div className="text-center">
                <div className="text-5xl font-bold text-foreground">{Math.round(wpm)}</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wider mt-1">WPM</div>
            </div>
            <div className="text-center">
                <div className="text-5xl font-bold text-foreground">{Math.round(accuracy)}%</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wider mt-1">Accuracy</div>
            </div>
        </div>
    );
}
