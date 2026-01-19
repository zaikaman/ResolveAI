/**
 * DebtList component - Display all debts with summary
 * Design aligned with landing page styling
 */

import { Plus, CreditCard, TrendingUp, PiggyBank } from 'lucide-react';
import { DebtCard } from './DebtCard';
import { Button } from '../common/Button';
import { Card, CardContent } from '../common/Card';
import type { Debt, DebtSummary } from '../../stores/debtStore';

interface DebtListProps {
    debts: Debt[];
    summary: DebtSummary | null;
    encryptionKey: string;
    onAddDebt: () => void;
    onEditDebt: (debt: Debt) => void;
    onDeleteDebt: (debt: Debt) => void;
    onMarkPaidOff: (debt: Debt) => void;
    loading?: boolean;
}

export function DebtList({
    debts,
    summary,
    encryptionKey,
    onAddDebt,
    onEditDebt,
    onDeleteDebt,
    onMarkPaidOff,
    loading = false,
}: DebtListProps) {
    if (loading) {
        return (
            <div className="space-y-6">
                {/* Summary skeleton */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {[1, 2, 3].map(i => (
                        <Card key={i} className="animate-pulse">
                            <CardContent className="py-4">
                                <div className="h-4 bg-slate-200 rounded w-1/3 mb-2" />
                                <div className="h-8 bg-slate-200 rounded w-1/2" />
                            </CardContent>
                        </Card>
                    ))}
                </div>
                {/* Cards skeleton */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[1, 2, 3].map(i => (
                        <Card key={i} className="animate-pulse">
                            <CardContent className="py-6 space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 bg-slate-200 rounded-lg" />
                                    <div className="flex-1">
                                        <div className="h-4 bg-slate-200 rounded w-2/3 mb-2" />
                                        <div className="h-3 bg-slate-200 rounded w-1/2" />
                                    </div>
                                </div>
                                <div className="h-8 bg-slate-200 rounded w-1/2" />
                                <div className="grid grid-cols-3 gap-4 pt-4">
                                    {[1, 2, 3].map(j => (
                                        <div key={j} className="h-8 bg-slate-200 rounded" />
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }

    // Empty state
    if (debts.length === 0) {
        return (
            <Card className="text-center py-16">
                <CardContent>
                    <div className="mx-auto w-16 h-16 bg-main2 rounded-full flex items-center justify-center mb-4">
                        <CreditCard className="h-8 w-8 text-main" />
                    </div>
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">No debts yet</h3>
                    <p className="text-slate-500 mb-6 max-w-sm mx-auto">
                        Start by adding your first debt. We'll help you create an optimized repayment plan.
                    </p>
                    <Button onClick={onAddDebt} leftIcon={<Plus className="h-4 w-4" />}>
                        Add Your First Debt
                    </Button>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-6">
            {/* Summary cards */}
            {summary && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <Card className="bg-gradient-to-br from-main3 to-white border-main/20">
                        <CardContent className="py-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-main2 rounded-lg">
                                    <CreditCard className="h-5 w-5 text-main" />
                                </div>
                                <div>
                                    <p className="text-sm text-slate-500">Total Debts</p>
                                    <p className="text-2xl font-bold text-slate-900">{summary.total_debts}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-gradient-to-br from-blue-50 to-white border-blue-200/50">
                        <CardContent className="py-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <TrendingUp className="h-5 w-5 text-blue-600" />
                                </div>
                                <div>
                                    <p className="text-sm text-slate-500">Active</p>
                                    <p className="text-2xl font-bold text-slate-900">{summary.active_debts}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="bg-gradient-to-br from-progress-50 to-white border-progress-200/50">
                        <CardContent className="py-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-progress-100 rounded-lg">
                                    <PiggyBank className="h-5 w-5 text-progress-600" />
                                </div>
                                <div>
                                    <p className="text-sm text-slate-500">Paid Off</p>
                                    <p className="text-2xl font-bold text-progress-600">{summary.paid_off_debts}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Add button */}
            <div className="flex justify-end">
                <Button onClick={onAddDebt} leftIcon={<Plus className="h-4 w-4" />}>
                    Add Debt
                </Button>
            </div>

            {/* Debt cards grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {debts.map(debt => (
                    <DebtCard
                        key={debt.id}
                        debt={debt}
                        encryptionKey={encryptionKey}
                        onEdit={onEditDebt}
                        onDelete={onDeleteDebt}
                        onMarkPaidOff={onMarkPaidOff}
                    />
                ))}
            </div>
        </div>
    );
}
