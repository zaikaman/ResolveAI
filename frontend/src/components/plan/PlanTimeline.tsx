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
import { formatCompactNumber, formatCurrency, formatDate } from '../../utils/formatting';

interface PlanTimelineProps {
    projections: PlanProjection[];
    className?: string;
}

export function PlanTimeline({ projections, className }: PlanTimelineProps) {
    const chartData = useMemo(() => {
        return projections.map((p) => ({
            month: p.month,
            date: formatDate(p.date, { month: 'short', year: '2-digit' }),
            remaining: p.total_remaining,
            interestPaid: p.cumulative_interest_paid,
            principalPaid: p.cumulative_principal_paid,
        }));
    }, [projections]);

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-white p-4 rounded-lg shadow-lg border border-slate-200">
                    <p className="font-semibold text-slate-900 mb-2">{label}</p>
                    <div className="space-y-2">
                        <div className="flex items-center justify-between gap-8">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-progress-500" />
                                <span className="text-sm text-slate-600">Balance</span>
                            </div>
                            <span className="text-sm font-bold text-slate-900">{formatCurrency(payload[0].value)}</span>
                        </div>
                        {payload[1] && (
                            <div className="flex items-center justify-between gap-8">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-progress-600" />
                                    <span className="text-sm text-slate-600">Principal Paid</span>
                                </div>
                                <span className="text-sm font-bold text-slate-900">{formatCurrency(payload[1]?.value)}</span>
                            </div>
                        )}
                        {payload[2] && (
                            <div className="flex items-center justify-between gap-8">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-warm-500" />
                                    <span className="text-sm text-slate-600">Interest Paid</span>
                                </div>
                                <span className="text-sm font-bold text-slate-900">{formatCurrency(payload[2]?.value)}</span>
                            </div>
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
                                <linearGradient id="colorRemaining" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#2D9F75" stopOpacity={0.1}/>
                                    <stop offset="95%" stopColor="#2D9F75" stopOpacity={0}/>
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                            <XAxis 
                                dataKey="date" 
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#64748B', fontSize: 12 }}
                                dy={10}
                            />
                            <YAxis 
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: '#64748B', fontSize: 12 }}
                                tickFormatter={(value) => formatCompactNumber(value)}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="remaining"
                                stroke="#2563EB"
                                strokeWidth={2}
                                fill="url(#colorRemaining)"
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
