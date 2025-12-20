import type { Keystroke } from '@/types/game';
import type { NgramCalculation, NgramStats, NgramType } from '@/types/ngram';

/**
 * Extract n-grams from a game using Inter-Key Interval (IKI) method
 * Uses the expected sentence as the source of n-grams, but calculates timing from actual keystrokes
 */
export function extractNgramsFromGame(
    sentence: string,
    keystrokes: Keystroke[],
    ngramSize: 2 | 3 | 4
): NgramCalculation[] {
    const results: NgramCalculation[] = [];
    const sentenceChars = sentence.split('');
    
    // Create a map of expected position -> keystroke
    // We track the position in the expected sentence
    const keystrokesByPosition = new Map<number, Keystroke[]>();
    
    let currentExpectedPos = 0;
    
    for (const ks of keystrokes) {
        // Store all keystrokes at this expected position
        if (!keystrokesByPosition.has(currentExpectedPos)) {
            keystrokesByPosition.set(currentExpectedPos, []);
        }
        keystrokesByPosition.get(currentExpectedPos)!.push(ks);
        
        // Move to next expected position only if this keystroke was correct
        if (ks.isCorrect && ks.expectedKey === sentenceChars[currentExpectedPos]) {
            currentExpectedPos++;
        }
    }
    
    // Extract n-grams from expected sentence
    for (let i = 0; i <= sentenceChars.length - ngramSize; i++) {
        const ngram = sentenceChars.slice(i, i + ngramSize).join('');
        
        // Get the first keystroke at each position for this n-gram
        const ngramKeystrokes: Keystroke[] = [];
        let hasError = false;
        let allPositionsHaveKeystrokes = true;
        
        for (let j = 0; j < ngramSize; j++) {
            const position = i + j;
            const keystrokesAtPos = keystrokesByPosition.get(position);
            
            if (keystrokesAtPos && keystrokesAtPos.length > 0) {
                // Use the first keystroke at this position (the actual attempt)
                const keystroke = keystrokesAtPos[0];
                ngramKeystrokes.push(keystroke);
                
                if (!keystroke.isCorrect) {
                    hasError = true;
                }
            } else {
                allPositionsHaveKeystrokes = false;
                break;
            }
        }
        
        // Only calculate duration if we have keystrokes for all positions
        if (allPositionsHaveKeystrokes && ngramKeystrokes.length === ngramSize) {
            // Calculate IKI (Inter-Key Interval)
            let totalInterval = 0;
            
            for (let j = 1; j < ngramKeystrokes.length; j++) {
                const interval = ngramKeystrokes[j].timestamp - ngramKeystrokes[j - 1].timestamp;
                totalInterval += interval;
            }
            
            // For bigrams, use the direct interval
            // For trigrams/quadgrams, use average interval
            const duration = ngramSize === 2 
                ? totalInterval 
                : totalInterval / (ngramSize - 1);
            
            results.push({
                ngram,
                duration,
                hadError: hasError,
            });
        }
    }
    
    return results;
}

/**
 * Calculate aggregate statistics for n-grams
 */
export function calculateNgramStats(
    calculations: NgramCalculation[]
): NgramStats[] {
    // Group by n-gram
    const grouped = new Map<string, NgramCalculation[]>();
    
    for (const calc of calculations) {
        if (!grouped.has(calc.ngram)) {
            grouped.set(calc.ngram, []);
        }
        grouped.get(calc.ngram)!.push(calc);
    }
    
    // Calculate stats for each n-gram
    const stats: NgramStats[] = [];
    
    for (const [ngram, calcs] of grouped.entries()) {
        const durations = calcs.map(c => c.duration).sort((a, b) => a - b);
        const errorCount = calcs.filter(c => c.hadError).length;
        
        // Average
        const avgTime = durations.reduce((a, b) => a + b, 0) / durations.length;
        
        // Median
        const mid = Math.floor(durations.length / 2);
        const medianTime = durations.length % 2 === 0
            ? (durations[mid - 1] + durations[mid]) / 2
            : durations[mid];
        
        // Standard deviation
        const variance = durations.reduce((sum, d) => sum + Math.pow(d - avgTime, 2), 0) / durations.length;
        const stdDev = Math.sqrt(variance);
        
        // 90th percentile
        const p90Index = Math.floor(durations.length * 0.9);
        const percentile90 = durations[p90Index] || durations[durations.length - 1];
        
        // Error rate
        const errorRate = (errorCount / calcs.length) * 100;
        
        stats.push({
            ngram,
            count: calcs.length,
            avgTime: Math.round(avgTime),
            medianTime: Math.round(medianTime),
            stdDev: Math.round(stdDev),
            percentile90: Math.round(percentile90),
            errorRate: Math.round(errorRate * 10) / 10, // 1 decimal place
        });
    }
    
    return stats;
}

/**
 * Get the n-gram size from the type
 */
export function getNgramSize(type: NgramType): 2 | 3 | 4 {
    switch (type) {
        case 'bigram':
            return 2;
        case 'trigram':
            return 3;
        case 'quadgram':
            return 4;
    }
}
