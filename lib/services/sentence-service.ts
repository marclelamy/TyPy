import { readFile } from 'fs/promises';
import { join } from 'path';
import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { generateObject } from 'ai';
import { z } from 'zod';
import type { GameConfig } from '@/types/game';
import type { NgramStats } from '@/types/ngram';

const openrouterClient = createOpenRouter({
    apiKey: process.env.NODE_ENV === 'development' 
        ? process.env.OPENROUTER_API_KEY_DEV 
        : process.env.OPENROUTER_API_KEY
});

const sentenceSchema = z.object({
    sentence: z.string().describe('A coherent paragraph made only from the provided words. No punctuation. No capital letters. All lowercase. Use minimal words possible while using all provided words.')
});

const vocabularySchema = z.object({
    word: z.string().describe('The vocabulary word'),
    definition: z.string().describe('A clear definition of the word. No punctuation. No capital letters. All lowercase.'),
    examples: z.array(z.string()).length(3).describe('Three short example sentences using the word. No punctuation. No capital letters. All lowercase.'),
    synonyms: z.array(z.string()).min(5).max(6).describe('Five to six synonyms for the word.')
});

const DATA_DIR = join(process.cwd(), 'public', 'data', 'words');

export async function loadWordList(difficulty: string): Promise<string[]> {
    let filePath: string;
    
    if (difficulty === 'easy') {
        filePath = join(DATA_DIR, 'wikipedia_1000.txt');
    } else if (difficulty === 'medium') {
        filePath = join(DATA_DIR, 'google-10000-english.txt');
    } else if (difficulty === 'hard') {
        filePath = join(DATA_DIR, 'nltk_corpus_words_250k.txt');
    } else {
        throw new Error(`Unknown difficulty: ${difficulty}`);
    }
    
    try {
        const content = await readFile(filePath, 'utf-8');
        const words = content.split('\n').filter(w => w.trim().length > 0);
        
        if (words.length === 0) {
            throw new Error(`Word list file is empty: ${filePath}`);
        }
        
        // Remove duplicates and shuffle
        const uniqueWords = Array.from(new Set(words));
        return shuffleArray(uniqueWords);
    } catch (error) {
        throw new Error(`Failed to load word list for difficulty ${difficulty}: ${error instanceof Error ? error.message : String(error)}`);
    }
}

function shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

async function selectWords(config: GameConfig): Promise<string[]> {
    const wordList = await loadWordList(config.difficulty);
    
    // Filter by word length
    const filteredWords = wordList.filter(
        word => word.length >= config.wordLengthMin && word.length <= config.wordLengthMax
    );
    
    if (filteredWords.length === 0) {
        throw new Error(`No words found matching length criteria (${config.wordLengthMin}-${config.wordLengthMax} characters)`);
    }
    
    // Select random words
    const selectedWords: string[] = [];
    const usedIndices = new Set<number>();
    for (let i = 0; i < config.wordCount; i++) {
        let randomIndex;
        do {
            randomIndex = Math.floor(Math.random() * filteredWords.length);
        } while (usedIndices.has(randomIndex) && usedIndices.size < filteredWords.length);
        usedIndices.add(randomIndex);
        selectedWords.push(filteredWords[randomIndex]);
    }
    
    return selectedWords;
}

/**
 * Select words with weighting based on user's weak n-grams.
 * Words containing n-grams the user is slow at or makes errors on get higher priority.
 */
async function selectWordsWithWeights(
    config: GameConfig,
    ngramStats: NgramStats[]
): Promise<string[]> {
    const wordList = await loadWordList(config.difficulty);
    
    // Filter by word length
    const filteredWords = wordList.filter(
        word => word.length >= config.wordLengthMin && word.length <= config.wordLengthMax
    );
    
    if (filteredWords.length === 0) {
        throw new Error(`No words found matching length criteria (${config.wordLengthMin}-${config.wordLengthMax} characters)`);
    }
    
    // If no n-gram stats, fall back to random selection
    if (ngramStats.length === 0) {
        return selectWords(config);
    }
    
    // Filter out invalid stats (missing or zero median times)
    const validStats = ngramStats.filter(s => s.medianTime && s.medianTime > 0);
    if (validStats.length === 0) {
        return selectWords(config);
    }
    
    // Calculate baseline median time (average of all median times)
    const allMedianTimes = validStats.map(s => s.medianTime);
    const baselineMedian = allMedianTimes.reduce((a, b) => a + b, 0) / allMedianTimes.length;
    
    // Safeguard: if baseline is invalid, fall back to random
    if (!baselineMedian || baselineMedian <= 0 || !isFinite(baselineMedian)) {
        return selectWords(config);
    }
    
    // Create a map of n-gram → score (higher = user is slower/more errors)
    const ngramScores = new Map<string, number>();
    for (const stat of validStats) {
        // Quadratic scaling: how much slower than baseline?
        // slowness=2 (twice as slow) → timeScore=4
        // slowness=3 (3x slower) → timeScore=9
        const slowness = stat.medianTime / baselineMedian;
        const timeScore = Math.pow(slowness, 2);
        
        // Error rate multiplier: 10% errors → 1.5x, 20% → 2x, 50% → 3.5x
        const errorMultiplier = 1 + ((stat.errorRate || 0) / 100) * 5;
        
        // Final score: quadratic time × error multiplier × baseline (for units)
        const score = timeScore * errorMultiplier * baselineMedian;
        ngramScores.set(stat.ngram.toLowerCase(), score);
    }
    
    // Score each word based on how many "problem" n-grams it contains
    const wordScores = filteredWords.map(word => {
        let score = 0;
        const lowerWord = word.toLowerCase();
        
        // Check trigrams in the word
        for (let i = 0; i <= lowerWord.length - 3; i++) {
            const trigram = lowerWord.slice(i, i + 3);
            score += ngramScores.get(trigram) || 0;
        }
        
        // Check quadgrams in the word
        for (let i = 0; i <= lowerWord.length - 4; i++) {
            const quadgram = lowerWord.slice(i, i + 4);
            score += ngramScores.get(quadgram) || 0;
        }
        
        return { word, score };
    });
    
    // Sort by score (highest first - these are the words with problem n-grams)
    wordScores.sort((a, b) => b.score - a.score);
    
    // Mix: take ~70% high-score words + ~30% random for variety
    const highScoreCount = Math.floor(config.wordCount * 0.7);
    const randomCount = config.wordCount - highScoreCount;
    
    // Get unique high-score words
    const highScoreWords = wordScores
        .slice(0, Math.min(highScoreCount * 2, wordScores.length)) // Get more than needed
        .filter(w => w.score > 0); // Only words that actually have problem n-grams
    
    // If we don't have enough high-score words, fill with random
    const selectedHighScore = shuffleArray(highScoreWords)
        .slice(0, Math.min(highScoreCount, highScoreWords.length));
    
    // Get random words from the rest (excluding already selected)
    const usedWords = new Set(selectedHighScore.map(w => w.word));
    const remainingWords = wordScores.filter(w => !usedWords.has(w.word));
    const randomWords = shuffleArray(remainingWords).slice(0, randomCount);
    
    // Combine and shuffle the final selection
    const finalWords = [
        ...selectedHighScore.map(w => w.word),
        ...randomWords.map(w => w.word),
    ];
    
    // If we still don't have enough words, pad with random
    while (finalWords.length < config.wordCount && remainingWords.length > 0) {
        const word = remainingWords.pop()?.word;
        if (word && !usedWords.has(word)) {
            finalWords.push(word);
            usedWords.add(word);
        }
    }
    
    return shuffleArray(finalWords);
}

export async function generateSentenceWithLLM(
    config: GameConfig,
    ngramStats?: NgramStats[]
): Promise<string> {
    // Use weighted selection if n-gram stats provided, otherwise random
    const selectedWords = ngramStats && ngramStats.length > 0
        ? await selectWordsWithWeights(config, ngramStats)
        : await selectWords(config);
    // Convert all words to lowercase for consistency
    const lowercaseWords = selectedWords.map(word => word.toLowerCase());
    const wordsString = lowercaseWords.join(', ');
    
    // Get model from env or use default
    const model = process.env.OPENROUTER_MODEL || 'openai/gpt-4o-mini';
    
    // Generate sentence using OpenRouter
    const result = await generateObject({
        model: openrouterClient(model),
        schema: sentenceSchema,
        messages: [
            {
                role: 'system',
                content: 'You are a helpful assistant that creates natural, coherent paragraphs using only the words provided. Use each word at least once. No punctuation. No capital letters. All lowercase. Use minimal words possible.'
            },
            {
                role: 'user',
                content: `Create a natural paragraph using only these words: ${wordsString}. Use each word at least once. No punctuation. No capital letters. All lowercase. Use minimal words possible while making it coherent and readable.`
            }
        ],
        experimental_repairText: async ({ text, error }) => {
            // Simple repair - just return the text as-is if repair fails
            try {
                const jsonrepair = (await import('jsonrepair')).default;
                return jsonrepair(text);
            } catch {
                return text;
            }
        },
    });
    
    // Ensure the result is lowercase (in case model adds capitals)
    return result.object.sentence.toLowerCase();
}

export async function generateSentence(
    config: GameConfig,
    ngramStats?: NgramStats[]
): Promise<string> {
    // Use weighted selection if n-gram stats provided, otherwise random
    const selectedWords = ngramStats && ngramStats.length > 0
        ? await selectWordsWithWeights(config, ngramStats)
        : await selectWords(config);
    return selectedWords.join(' ');
}

export async function generateVocabularySentence(): Promise<string> {
    // Load hard words and common words to filter out common ones
    const hardWords = await loadWordList('hard');
    const commonWordsList = await loadWordList('easy');
    const commonWordsSet = new Set(commonWordsList.map(w => w.toLowerCase()));
    
    // Filter to get uncommon words (not in common list, reasonable length)
    const uncommonWords = hardWords.filter(w => {
        const lower = w.toLowerCase();
        return !commonWordsSet.has(lower) && 
               w.length >= 5 && 
               w.length <= 12 &&
               /^[a-z]+$/i.test(w); // Only alphabetic words
    });
    
    if (uncommonWords.length === 0) {
        throw new Error('No uncommon words found');
    }
    
    // Pick a random word
    const randomWord = uncommonWords[Math.floor(Math.random() * uncommonWords.length)];
    
    const model = process.env.OPENROUTER_MODEL || 'openai/gpt-4o-mini';
    
    // Generate vocabulary content using OpenRouter
    const result = await generateObject({
        model: openrouterClient(model),
        schema: vocabularySchema,
        messages: [
            {
                role: 'system',
                content: 'You are a vocabulary teacher. Generate content to help learn a word. No punctuation. No capital letters. All lowercase.'
            },
            {
                role: 'user',
                content: `Generate vocabulary content for the word "${randomWord}". Include a clear definition, 3 short example sentences, and 5-6 synonyms. No punctuation. No capital letters. All lowercase.`
            }
        ],
        experimental_repairText: async ({ text, error }) => {
            try {
                const jsonrepair = (await import('jsonrepair')).default;
                return jsonrepair(text);
            } catch {
                return text;
            }
        },
    });
    
    const { definition, examples, synonyms } = result.object;
    
    // Format: definition + examples + synonyms
    const formattedText = [
        definition,
        ...examples,
        `synonyms ${synonyms.join(' ')}`
    ].join(' ');
    
    // Ensure everything is lowercase (in case model adds capitals)
    return formattedText.toLowerCase();
}
