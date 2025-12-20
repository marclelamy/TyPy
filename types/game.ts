export interface GameConfig {
    difficulty: 'easy' | 'medium' | 'hard';
    wordCount: number;
    wordLengthMin: number;
    wordLengthMax: number;
    generationMode?: 'paragraph' | 'vocabulary' | 'random'; // Default 'paragraph'
    learnFromMistakes?: boolean; // Default false - weight words based on user's weak n-grams
}

export interface Keystroke {
    key: string;
    expectedKey: string;
    isCorrect: boolean;
    timestamp: number;
    shiftPressed?: 'left' | 'right' | null;
}

export interface TypedChar {
    key: string;
    expectedKey: string;
    isCorrect: boolean;
}

export interface GameState {
    status: 'idle' | 'loading' | 'ready' | 'playing' | 'finished';
    gameId: string | null;
    sentence: string;
    currentIndex: number;
    keystrokes: Keystroke[]; // All keystrokes for analytics
    typedChars: Record<number, TypedChar>; // Latest typed char at each position for display
    startTime: number | null;
}

export interface ChartDataPoint {
    wordIndex: number;
    wpm: number;
    raw: number;
    errors: number;
}

export interface GameResult {
    wpm: number;
    accuracy: number;
    duration: number;
    correctCount: number;
    errorCount: number;
    chartData?: ChartDataPoint[];
}
