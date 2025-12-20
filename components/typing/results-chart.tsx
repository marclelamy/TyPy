'use client';

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    ReferenceDot,
    CartesianGrid,
} from 'recharts';
import type { ChartDataPoint } from '@/types/game';

interface ResultsChartProps {
    data: ChartDataPoint[];
}

interface CustomTooltipProps {
    active?: boolean;
    payload?: Array<{
        payload: ChartDataPoint;
    }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
    if (!active || !payload || payload.length === 0) return null;

    const data = payload[0].payload;

    return (
        <div className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 shadow-lg">
            <div className="text-zinc-400 text-sm mb-1">{data.wordIndex}</div>
            <div className="space-y-0.5 text-sm">
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-red-500 rounded-sm" />
                    <span className="text-zinc-400">errors:</span>
                    <span className="text-white font-medium">{data.errors}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-emerald-500 rounded-sm" />
                    <span className="text-zinc-400">wpm:</span>
                    <span className="text-white font-medium">{data.wpm}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-yellow-500 rounded-sm" />
                    <span className="text-zinc-400">raw:</span>
                    <span className="text-white font-medium">{data.raw}</span>
                </div>
            </div>
        </div>
    );
}

export function ResultsChart({ data }: ResultsChartProps) {
    if (data.length === 0) return null;

    // Calculate Y axis domain with some padding
    const allWpmValues = data.flatMap(d => [d.wpm, d.raw]);
    const maxWpm = Math.max(...allWpmValues);
    const minWpm = Math.min(...allWpmValues);
    const yPadding = Math.max(10, (maxWpm - minWpm) * 0.1);

    return (
        <div className="w-full h-48">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart
                    data={data}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                >
                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#3f3f46"
                        horizontal={true}
                        vertical={false}
                    />
                    <XAxis
                        dataKey="wordIndex"
                        stroke="#71717a"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                    />
                    <YAxis
                        stroke="#71717a"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                        domain={[Math.max(0, minWpm - yPadding), maxWpm + yPadding]}
                        tickFormatter={(value) => `${Math.round(value)}`}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    
                    {/* Raw WPM line (dashed, grey) */}
                    <Line
                        type="monotone"
                        dataKey="raw"
                        stroke="#a1a1aa"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={false}
                        activeDot={{ r: 4, fill: '#a1a1aa' }}
                    />
                    
                    {/* WPM line (solid, yellow/gold) */}
                    <Line
                        type="monotone"
                        dataKey="wpm"
                        stroke="#eab308"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4, fill: '#eab308' }}
                    />

                    {/* Error markers */}
                    {data.map((point, index) =>
                        point.errors > 0 ? (
                            <ReferenceDot
                                key={index}
                                x={point.wordIndex}
                                y={point.wpm}
                                r={4}
                                fill="#ef4444"
                                stroke="none"
                            />
                        ) : null
                    )}
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
