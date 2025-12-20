export type NgramType = 'bigram' | 'trigram' | 'quadgram';

export interface NgramCalculation {
    ngram: string;
    duration: number;  // IKI time in ms
    hadError: boolean;
}

export interface NgramStats {
    ngram: string;
    count: number;
    avgTime: number;
    medianTime: number;
    stdDev: number;
    percentile90: number;
    errorRate: number;
}
