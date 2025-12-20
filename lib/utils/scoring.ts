import type { Keystroke, ChartDataPoint } from '@/types/game';

export function calcWpm(correctKeyCount: number, durationMs: number): number {
    if (durationMs <= 0) return 0;
    const minutes = durationMs / 60000;
    const wpm = (correctKeyCount / 5) / minutes; // Average word is 5 characters
    return Math.round(wpm * 100) / 100;
}

export function calcAccuracy(correct: number, total: number): number {
    if (total === 0) return 0;
    return Math.round((correct / total) * 10000) / 100;
}

export function calcDuration(keystrokes: Keystroke[]): number {
    if (keystrokes.length < 2) return 0;
    const first = keystrokes[0].timestamp;
    const last = keystrokes[keystrokes.length - 1].timestamp;
    return last - first;
}

/**
 * Process keystrokes into per-word chart data for visualization.
 * Each data point represents stats at word completion.
 */
export function calcChartData(keystrokes: Keystroke[], sentence: string): ChartDataPoint[] {
    if (keystrokes.length === 0 || !sentence) return [];

    const chartData: ChartDataPoint[] = [];
    const startTime = keystrokes[0].timestamp;
    
    // Find word boundaries (spaces) in the sentence
    const wordEndIndices: number[] = [];
    for (let i = 0; i < sentence.length; i++) {
        if (sentence[i] === ' ' || i === sentence.length - 1) {
            wordEndIndices.push(i);
        }
    }

    // Track cumulative stats
    let keystrokeIndex = 0;
    let charPosition = 0;
    let totalCorrect = 0;
    let totalKeystrokes = 0;

    for (let wordIndex = 0; wordIndex < wordEndIndices.length; wordIndex++) {
        const wordEndPos = wordEndIndices[wordIndex];
        let wordErrors = 0;

        // Process keystrokes until we reach the end of this word
        while (keystrokeIndex < keystrokes.length && charPosition <= wordEndPos) {
            const ks = keystrokes[keystrokeIndex];
            
            if (ks.key === 'Backspace') {
                charPosition = Math.max(0, charPosition - 1);
            } else if (ks.key !== 'Escape') {
                if (ks.isCorrect) {
                    totalCorrect++;
                } else {
                    wordErrors++;
                }
                totalKeystrokes++;
                charPosition++;
            }
            
            keystrokeIndex++;
            
            // Check if we've completed this word
            if (charPosition > wordEndPos) {
                break;
            }
        }

        // Calculate stats at this word
        if (keystrokeIndex > 0) {
            const currentTime = keystrokes[Math.min(keystrokeIndex - 1, keystrokes.length - 1)].timestamp;
            const elapsed = currentTime - startTime;

            const wpm = calcWpm(totalCorrect, elapsed);
            const raw = calcWpm(totalKeystrokes, elapsed);

            chartData.push({
                wordIndex: wordIndex + 1,
                wpm: Math.round(wpm),
                raw: Math.round(raw),
                errors: wordErrors,
            });
        }
    }

    return chartData;
}
