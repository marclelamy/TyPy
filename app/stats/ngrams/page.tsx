'use client';

import { useEffect, useState, useMemo } from 'react';
import { useVisitorId } from '@/hooks/use-visitor-id';
import { useNgramCache } from '@/hooks/use-ngram-cache';
import { useDataTable } from '@/hooks/use-data-table';
import { DataTable } from '@/components/data-table/data-table';
import { DataTableToolbar } from '@/components/data-table/data-table-toolbar';
import { DataTableColumnHeader } from '@/components/data-table/data-table-column-header';
import type { ColumnDef } from '@tanstack/react-table';
import type { NgramStats, NgramType } from '@/types/ngram';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowLeft, RefreshCw } from 'lucide-react';

function getColorForTime(time: number, allTimes: number[]): string {
    if (allTimes.length === 0) return 'text-foreground';
    
    const sorted = [...allTimes].sort((a, b) => a - b);
    const percentile = (sorted.indexOf(time) / sorted.length) * 100;
    
    // Green (fast) -> Yellow -> Orange -> Red (slow)
    if (percentile < 25) return 'text-green-500';
    if (percentile < 50) return 'text-yellow-500';
    if (percentile < 75) return 'text-orange-500';
    return 'text-red-500';
}

function formatTimeAgo(timestamp: number): string {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

export default function NgramsStatsPage() {
    const { visitorId, loading: visitorLoading } = useVisitorId();
    const { getCached, refreshInBackground } = useNgramCache(visitorId);
    const [ngramType, setNgramType] = useState<NgramType>('bigram');
    const [isRefreshing, setIsRefreshing] = useState(false);
    
    // Get cached data
    const cached = getCached();
    const allData = {
        bigrams: cached?.bigrams || [],
        trigrams: cached?.trigrams || [],
        quadgrams: cached?.quadgrams || [],
    };
    const gamesAnalyzed = cached?.gamesAnalyzed || 0;
    const fetchedAt = cached?.fetchedAt;
    
    // Trigger a refresh if no cached data
    useEffect(() => {
        if (visitorId && !cached) {
            refreshInBackground();
        }
    }, [visitorId, cached, refreshInBackground]);
    
    const handleRefresh = () => {
        setIsRefreshing(true);
        refreshInBackground();
        // Give it a moment to fetch, then re-render
        setTimeout(() => setIsRefreshing(false), 2000);
    };
    
    // Get the current data based on selected n-gram type
    const data = ngramType === 'bigram' 
        ? allData.bigrams 
        : ngramType === 'trigram' 
        ? allData.trigrams 
        : allData.quadgrams;
    
    const columns = useMemo<ColumnDef<NgramStats>[]>(() => {
        const allMedianTimes = data.map(d => d.medianTime);
        const allAvgTimes = data.map(d => d.avgTime);
        const allP90Times = data.map(d => d.percentile90);
        
        return [
            {
                id: 'ngram',
                accessorKey: 'ngram',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} label="Pattern" />
                ),
                cell: ({ row }) => (
                    <div className="font-mono font-bold text-lg">
                        {row.getValue('ngram')}
                    </div>
                ),
                meta: {
                    label: 'Pattern',
                },
            },
            {
                id: 'count',
                accessorKey: 'count',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} label="Count" />
                ),
                cell: ({ row }) => (
                    <div className="text-center">{row.getValue('count')}</div>
                ),
                meta: {
                    label: 'Count',
                },
            },
            {
                id: 'medianTime',
                accessorKey: 'medianTime',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} label="Median Time" />
                ),
                cell: ({ row }) => {
                    const time = row.getValue('medianTime') as number;
                    const color = getColorForTime(time, allMedianTimes);
                    return (
                        <div className={`text-center font-semibold ${color}`}>
                            {time}ms
                        </div>
                    );
                },
                meta: {
                    label: 'Median Time',
                },
            },
            {
                id: 'avgTime',
                accessorKey: 'avgTime',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} label="Avg Time" />
                ),
                cell: ({ row }) => {
                    const time = row.getValue('avgTime') as number;
                    const color = getColorForTime(time, allAvgTimes);
                    return (
                        <div className={`text-center font-semibold ${color}`}>
                            {time}ms
                        </div>
                    );
                },
                meta: {
                    label: 'Average Time',
                },
            },
            {
                id: 'percentile90',
                accessorKey: 'percentile90',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} label="90th %ile" />
                ),
                cell: ({ row }) => {
                    const time = row.getValue('percentile90') as number;
                    const color = getColorForTime(time, allP90Times);
                    return (
                        <div className={`text-center font-semibold ${color}`}>
                            {time}ms
                        </div>
                    );
                },
                meta: {
                    label: '90th Percentile',
                },
            },
            {
                id: 'stdDev',
                accessorKey: 'stdDev',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} label="Std Dev" />
                ),
                cell: ({ row }) => (
                    <div className="text-center text-muted-foreground">
                        ±{row.getValue('stdDev')}ms
                    </div>
                ),
                meta: {
                    label: 'Standard Deviation',
                },
            },
            {
                id: 'errorRate',
                accessorKey: 'errorRate',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} label="Error Rate" />
                ),
                cell: ({ row }) => {
                    const rate = row.getValue('errorRate') as number;
                    const color = rate > 20 ? 'text-red-500' : rate > 10 ? 'text-orange-500' : 'text-green-500';
                    return (
                        <div className={`text-center font-semibold ${color}`}>
                            {rate}%
                        </div>
                    );
                },
                meta: {
                    label: 'Error Rate',
                },
            },
        ];
    }, [data]);
    
    const { table } = useDataTable({
        data,
        columns,
        pageCount: Math.ceil(data.length / 200),
        initialState: {
            pagination: {
                pageIndex: 0,
                pageSize: 200,
            },
        },
    });
    
    if (visitorLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background text-foreground">
                <div>Loading...</div>
            </div>
        );
    }
    
    return (
        <div className="min-h-screen bg-background text-foreground p-4">
            <div className="max-w-7xl mx-auto space-y-6">
                <Link href="/stats">
                    <Button variant="ghost" size="sm" className="mb-2">
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Stats
                    </Button>
                </Link>
                
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-4xl font-bold">N-gram Analysis</h1>
                        <p className="text-muted-foreground mt-2">
                            Analyzing {gamesAnalyzed} most recent games
                            {fetchedAt && (
                                <span className="ml-2 text-xs" title={new Date(fetchedAt).toLocaleString()}>
                                    (cached {formatTimeAgo(fetchedAt)})
                                </span>
                            )}
                        </p>
                    </div>
                    
                    <div className="flex items-center gap-4">
                        <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={handleRefresh}
                            disabled={isRefreshing}
                        >
                            <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                            Refresh
                        </Button>
                        
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">Select n-gram:</span>
                            <Select value={ngramType} onValueChange={(value: string) => setNgramType(value as NgramType)}>
                                <SelectTrigger className="w-[180px]">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="bigram">Bigram (2 letters)</SelectItem>
                                    <SelectItem value="trigram">Trigram (3 letters)</SelectItem>
                                    <SelectItem value="quadgram">Quadgram (4 letters)</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </div>
                
                <Card>
                    <CardHeader>
                        <CardTitle>
                            {ngramType === 'bigram' ? 'Bigrams' : ngramType === 'trigram' ? 'Trigrams' : 'Quadgrams'}
                        </CardTitle>
                        <CardDescription>
                            Letter combinations sorted by median typing time (slowest first)
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {data.length === 0 ? (
                            <div className="text-center text-muted-foreground py-8 space-y-4">
                                <p>No data yet. Complete some typing tests to see your n-gram statistics.</p>
                                {!cached && (
                                    <Button variant="outline" onClick={handleRefresh} disabled={isRefreshing}>
                                        <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                                        Load from server
                                    </Button>
                                )}
                            </div>
                        ) : (
                            <DataTable table={table}>
                                <DataTableToolbar table={table} />
                            </DataTable>
                        )}
                    </CardContent>
                </Card>
                
                <div className="text-sm text-muted-foreground space-y-2">
                    <p><strong>Legend:</strong></p>
                    <ul className="list-disc list-inside space-y-1">
                        <li><span className="text-green-500">Green</span> = Fast (top 25%)</li>
                        <li><span className="text-yellow-500">Yellow</span> = Average (25-50%)</li>
                        <li><span className="text-orange-500">Orange</span> = Slow (50-75%)</li>
                        <li><span className="text-red-500">Red</span> = Very slow (bottom 25%)</li>
                    </ul>
                    <p className="mt-4">
                        <strong>Tip:</strong> Focus on improving the patterns highlighted in red and orange. 
                        These are the letter combinations that slow down your typing the most.
                    </p>
                </div>
            </div>
        </div>
    );
}
