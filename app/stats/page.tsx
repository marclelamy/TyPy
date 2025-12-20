'use client';

import { useEffect, useState } from 'react';
import { useVisitorId } from '@/hooks/use-visitor-id';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface Game {
    id: string;
    wpm: number | null;
    accuracy: number | null;
    duration: number | null;
    createdAt: Date;
}

interface AggregateStats {
    avgWpm: number;
    avgAccuracy: number;
    totalGames: number;
}

interface ImprovementRate {
    wpmPerHour: number | null;
    totalHoursPlayed: number;
    dataPoints: number;
}

export default function StatsPage() {
    const { visitorId, loading: visitorLoading } = useVisitorId();
    const [recentGames, setRecentGames] = useState<Game[]>([]);
    const [aggregateStats, setAggregateStats] = useState<AggregateStats | null>(null);
    const [improvementRate, setImprovementRate] = useState<ImprovementRate | null>(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        if (!visitorId) return;
        
        fetch(`/api/stats?visitorId=${visitorId}&limit=20`)
            .then(res => res.json())
            .then(data => {
                setRecentGames(data.recentGames || []);
                setAggregateStats(data.aggregateStats || null);
                setImprovementRate(data.improvementRate || null);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching stats:', err);
                setLoading(false);
            });
    }, [visitorId]);
    
    if (visitorLoading || loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background text-foreground">
                <div>Loading stats...</div>
            </div>
        );
    }
    
    return (
        <div className="min-h-screen bg-background text-foreground p-4">
            <div className="max-w-4xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <h1 className="text-4xl font-bold">Statistics</h1>
                    <Link href="/stats/ngrams">
                        <Button variant="outline">View N-gram Analysis</Button>
                    </Link>
                </div>
                
                {aggregateStats && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Overall Stats</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <div className="text-2xl font-bold">{Math.round(aggregateStats.avgWpm)}</div>
                                    <div className="text-sm text-muted-foreground">Avg WPM</div>
                                </div>
                                <div>
                                    <div className="text-2xl font-bold">{Math.round(aggregateStats.avgAccuracy)}%</div>
                                    <div className="text-sm text-muted-foreground">Avg Accuracy</div>
                                </div>
                                <div>
                                    <div className="text-2xl font-bold">{aggregateStats.totalGames}</div>
                                    <div className="text-sm text-muted-foreground">Total Games</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}
                
                {improvementRate && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Improvement Rate</CardTitle>
                            <CardDescription>WPM improvement per hour of practice (linear regression)</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <div className="text-2xl font-bold">
                                        {improvementRate.wpmPerHour !== null
                                            ? `${improvementRate.wpmPerHour >= 0 ? '+' : ''}${improvementRate.wpmPerHour.toFixed(1)}`
                                            : '—'}
                                    </div>
                                    <div className="text-sm text-muted-foreground">WPM / Hour</div>
                                </div>
                                <div>
                                    <div className="text-2xl font-bold">
                                        {improvementRate.totalHoursPlayed < 1
                                            ? `${Math.round(improvementRate.totalHoursPlayed * 60)}m`
                                            : `${improvementRate.totalHoursPlayed.toFixed(1)}h`}
                                    </div>
                                    <div className="text-sm text-muted-foreground">Total Time Played</div>
                                </div>
                                <div>
                                    <div className="text-2xl font-bold">{improvementRate.dataPoints}</div>
                                    <div className="text-sm text-muted-foreground">Games Analyzed</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}
                
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Games</CardTitle>
                        <CardDescription>Your latest typing tests</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {recentGames.length === 0 ? (
                            <div className="text-center text-muted-foreground py-8">No games yet</div>
                        ) : (
                            <div className="space-y-2">
                                {recentGames.map((game) => (
                                    <div
                                        key={game.id}
                                        className="flex justify-between items-center p-4 border border-border rounded-lg"
                                    >
                                        <div>
                                            <div className="text-sm text-muted-foreground">
                                                {new Date(game.createdAt).toLocaleDateString()}
                                            </div>
                                        </div>
                                        <div className="flex gap-6">
                                            {game.wpm !== null && (
                                                <div className="text-right">
                                                    <div className="font-bold">{Math.round(game.wpm)}</div>
                                                    <div className="text-xs text-muted-foreground">WPM</div>
                                                </div>
                                            )}
                                            {game.accuracy !== null && (
                                                <div className="text-right">
                                                    <div className="font-bold">{Math.round(game.accuracy)}%</div>
                                                    <div className="text-xs text-muted-foreground">Accuracy</div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
