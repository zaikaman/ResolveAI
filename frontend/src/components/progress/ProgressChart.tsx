/**
 * ProgressChart component - Debt reduction visualization over time
 */

import { useMemo } from 'react';
import {
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
    ReferenceLine,
    ComposedChart
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { formatCurrency } from '../../utils/formatting';
import type { Payment } from '../../services/paymentService';

interface ProgressChartProps {
    payments: Payment[];
    loading?: boolean;
    title?: string;
    showPrincipalInterest?: boolean;
}

interface ChartDataPoint {
    month: string;
    amount: number;
    principal: number;
    interest: number;
    count: number;
}

// Custom tooltip component
function CustomTooltip({ active, payload, label }: any) {
    if (!active || !payload || !payload.length) return null;

    return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-slate-200">
            <p className="font-semibold text-slate-900 mb-2">{label}</p>
            {payload.map((entry: any, index: number) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                    <div 
                        className="w-3 h-3 rounded-sm" 
                        style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-slate-600">{entry.name}:</span>
                    <span className="font-medium text-slate-900">
                        {formatCurrency(entry.value)}
                    </span>
                </div>
            ))}
        </div>
    );
}

export function ProgressChart({
    payments,
    loading = false,
    title = "Payment History",
    showPrincipalInterest = false
}: ProgressChartProps) {
    // Process payments into monthly aggregates
    const chartData = useMemo(() => {
        if (!payments || payments.length === 0) return [];

        const monthlyData: Record<string, ChartDataPoint> = {};

        payments.forEach(payment => {
            const date = new Date(payment.payment_date);
            const monthKey = date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });

            if (!monthlyData[monthKey]) {
                monthlyData[monthKey] = {
                    month: monthKey,
                    amount: 0,
                    principal: 0,
                    interest: 0,
                    count: 0
                };
            }

            monthlyData[monthKey].amount += payment.amount;
            // For now, assume all is principal (would need more data to split)
            monthlyData[monthKey].principal += payment.amount;
            monthlyData[monthKey].count += 1;
        });

        // Convert to array and sort by date
        return Object.values(monthlyData).sort((a, b) => {
            const dateA = new Date(a.month);
            const dateB = new Date(b.month);
            return dateA.getTime() - dateB.getTime();
        });
    }, [payments]);

    // Calculate average
    const averagePayment = useMemo(() => {
        if (chartData.length === 0) return 0;
        const total = chartData.reduce((sum, d) => sum + d.amount, 0);
        return total / chartData.length;
    }, [chartData]);

    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>{title}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-[300px] flex items-center justify-center">
                        <div className="animate-pulse flex flex-col items-center">
                            <div className="w-full h-48 bg-slate-100 rounded-lg mb-2" />
                            <div className="h-4 w-32 bg-slate-100 rounded" />
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (chartData.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>{title}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-[300px] flex items-center justify-center">
                        <div className="text-center">
                            <p className="text-slate-500 mb-2">No payment data yet</p>
                            <p className="text-sm text-slate-400">
                                Log your first payment to see your progress chart!
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart
                            data={chartData}
                            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis 
                                dataKey="month" 
                                tick={{ fill: '#64748b', fontSize: 12 }}
                                axisLine={{ stroke: '#e2e8f0' }}
                            />
                            <YAxis 
                                tick={{ fill: '#64748b', fontSize: 12 }}
                                axisLine={{ stroke: '#e2e8f0' }}
                                tickFormatter={(value) => `$${value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value}`}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend 
                                wrapperStyle={{ paddingTop: '20px' }}
                            />
                            
                            {/* Average line */}
                            <ReferenceLine 
                                y={averagePayment} 
                                stroke="#6366f1" 
                                strokeDasharray="3 3"
                                label={{ 
                                    value: `Avg: ${formatCurrency(averagePayment)}`, 
                                    position: 'right',
                                    fill: '#6366f1',
                                    fontSize: 11
                                }}
                            />

                            {showPrincipalInterest ? (
                                <>
                                    <Bar 
                                        dataKey="principal" 
                                        name="Principal" 
                                        stackId="a"
                                        fill="#22c55e" 
                                        radius={[0, 0, 0, 0]}
                                    />
                                    <Bar 
                                        dataKey="interest" 
                                        name="Interest" 
                                        stackId="a"
                                        fill="#f59e0b" 
                                        radius={[4, 4, 0, 0]}
                                    />
                                </>
                            ) : (
                                <Bar 
                                    dataKey="amount" 
                                    name="Payment Amount" 
                                    fill="#3b82f6" 
                                    radius={[4, 4, 0, 0]}
                                    maxBarSize={60}
                                />
                            )}
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>

                {/* Summary stats below chart */}
                <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-100">
                    <div className="text-center">
                        <p className="text-sm text-slate-500">Total Paid</p>
                        <p className="text-lg font-semibold text-slate-900">
                            {formatCurrency(chartData.reduce((sum, d) => sum + d.amount, 0))}
                        </p>
                    </div>
                    <div className="text-center">
                        <p className="text-sm text-slate-500">Avg/Month</p>
                        <p className="text-lg font-semibold text-slate-900">
                            {formatCurrency(averagePayment)}
                        </p>
                    </div>
                    <div className="text-center">
                        <p className="text-sm text-slate-500">Months Active</p>
                        <p className="text-lg font-semibold text-slate-900">
                            {chartData.length}
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

export default ProgressChart;
