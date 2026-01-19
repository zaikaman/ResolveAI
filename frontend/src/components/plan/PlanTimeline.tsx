/**
 * PlanTimeline component - Recharts line chart showing debt reduction over time
 * Design aligned with landing page styling
 */

import { useMemo } from 'react';
import {
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Area,
    AreaChart
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import type { PlanProjection } from '../../stores/planStore';

interface PlanTimelineProps {
    projections: PlanProjection[];
    className?: string;
}

export function PlanTimeline({ projections, className }: PlanTimelineProps) {
    const chartData = useMemo(() => {
        return projections.map((p) => ({
            month: p.month,
            date: new Date(p.date).toLocaleDateString('vi-VN', { month: 'short', year: '2-digit' }),
            remaining: p.total_remaining,
            interestPaid: p.cumulative_interest_paid,
            principalPaid: p.cumulative_principal_paid,
        }));
    }, [projections]);

    const formatCurrency = (value: number) => {
        if (value >= 1000000) {
            return `${(value / 1000000).toFixed(1)}M`;
        }
        if (value >= 1000) {
            return `${(value / 1000).toFixed(0)}K`;
        }
        return value.toString();
    };

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-white p-4 rounded-lg shadow-lg border border-slate-200">
                    <p className="font-semibold text-slate-900 mb-2">{label}</p>
                    <div className="space-y-1 text-sm">
                        <p className="text-main">
                            Remaining: <span className="font-semibold">{formatCurrency(payload[0]?.value)}</span>
                        </p>
                        {payload[1] && (
                            <p className="text-progress-600">
                                Principal Paid: <span className="font-semibold">{formatCurrency(payload[1]?.value)}</span>
                            </p>
                        )}
                        {payload[2] && (
                            <p className="text-warm-500">
                                Interest Paid: <span className="font-semibold">{formatCurrency(payload[2]?.value)}</span>
                            </p>
                        )}
                    </div>
                </div>
            );
        }
        return null;
    };

    if (projections.length === 0) {
        return (
            <Card className={className}>
                <CardHeader>
                    <CardTitle>Debt Payoff Timeline</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-64 flex items-center justify-center text-slate-500">
                        No projection data available
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle>Debt Payoff Timeline</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="remainingGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="principalGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis
                                dataKey="date"
                                tick={{ fontSize: 12, fill: '#64748b' }}
                                tickLine={{ stroke: '#e2e8f0' }}
                                axisLine={{ stroke: '#e2e8f0' }}
                                interval="preserveStartEnd"
                            />
                            <YAxis
                                tickFormatter={formatCurrency}
                                tick={{ fontSize: 12, fill: '#64748b' }}
                                tickLine={{ stroke: '#e2e8f0' }}
                                axisLine={{ stroke: '#e2e8f0' }}
                                width={60}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="remaining"
                                stroke="#2563EB"
                                strokeWidth={2}
                                fill="url(#remainingGradient)"
                                name="Remaining Debt"
                            />
                            <Area
                                type="monotone"
                                dataKey="principalPaid"
                                stroke="#22c55e"
                                strokeWidth={2}
                                fill="url(#principalGradient)"
                                name="Principal Paid"
                            />
                            <Line
                                type="monotone"
                                dataKey="interestPaid"
                                stroke="#f97316"
                                strokeWidth={2}
                                dot={false}
                                name="Interest Paid"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Legend */}
                <div className="flex items-center justify-center gap-6 mt-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-main" />
                        <span className="text-slate-600">Remaining Debt</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-progress-500" />
                        <span className="text-slate-600">Principal Paid</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-warm-500" />
                        <span className="text-slate-600">Interest Paid</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
