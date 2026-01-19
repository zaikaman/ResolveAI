/**
 * OCRFeedback component - Loading state, progress, and extracted data preview
 * Design aligned with landing page styling
 */

import { useState } from 'react';
import { Loader2, CheckCircle, AlertCircle, FileText, Plus, Edit2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Button } from '../common/Button';
import { cn } from '../../utils/cn';
import { formatCurrency } from '../../utils/formatting';
import type { ExtractedDebt } from '../../services/uploadService';

interface OCRFeedbackProps {
    status: 'idle' | 'processing' | 'completed' | 'failed';
    progress?: number;
    extractedDebts?: ExtractedDebt[];
    errorMessage?: string;
    onAddDebt?: (debt: ExtractedDebt) => void;
    onAddAll?: (debts: ExtractedDebt[]) => void;
    onEditDebt?: (debt: ExtractedDebt, index: number) => void;
    className?: string;
}

export function OCRFeedback({
    extractedDebts = [],
    status,
    progress = 0,
    errorMessage,
    onAddDebt,
    onAddAll,
    onEditDebt,
    className,
}: OCRFeedbackProps) {
    const [addedDebts, setAddedDebts] = useState<Set<number>>(new Set());

    const handleAddDebt = (debt: ExtractedDebt, index: number) => {
        if (onAddDebt) {
            onAddDebt(debt);
            setAddedDebts(prev => new Set([...prev, index]));
        }
    };

    const handleAddAll = () => {
        if (onAddAll) {
            onAddAll(extractedDebts.filter((_, i) => !addedDebts.has(i)));
            setAddedDebts(new Set(extractedDebts.map((_, i) => i)));
        }
    };

    // Idle state
    if (status === 'idle') {
        return null;
    }

    // Processing state
    if (status === 'processing') {
        return (
            <Card className={cn("text-center py-8", className)}>
                <CardContent>
                    <Loader2 className="h-12 w-12 text-main animate-spin mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">
                        Analyzing Your Document
                    </h3>
                    <p className="text-slate-500 mb-4">
                        Our AI is extracting debt information from your statement...
                    </p>
                    <div className="w-full max-w-xs mx-auto">
                        <div className="h-2 bg-main2 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-main rounded-full transition-all duration-300"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                        <p className="text-sm text-slate-500 mt-2">
                            {progress}% complete
                        </p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    // Failed state
    if (status === 'failed') {
        return (
            <Card className={cn("border-red-200 bg-red-50", className)}>
                <CardContent className="text-center py-8">
                    <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                        <AlertCircle className="h-8 w-8 text-red-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">
                        Failed to Extract Data
                    </h3>
                    <p className="text-slate-500 mb-4 max-w-sm mx-auto">
                        {errorMessage || 'We couldn\'t extract debt information from this document. Please try a clearer image or add debts manually.'}
                    </p>
                </CardContent>
            </Card>
        );
    }

    // Completed state with extracted debts
    return (
        <Card className={cn("border-progress-200", className)}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-progress-100 rounded-lg">
                            <CheckCircle className="h-5 w-5 text-progress-600" />
                        </div>
                        <div>
                            <CardTitle>Extracted Debts</CardTitle>
                            <p className="text-sm text-slate-500">
                                {extractedDebts.length} debt{extractedDebts.length !== 1 ? 's' : ''} found
                            </p>
                        </div>
                    </div>
                    {extractedDebts.length > 1 && onAddAll && addedDebts.size < extractedDebts.length && (
                        <Button onClick={handleAddAll} size="sm">
                            Add All
                        </Button>
                    )}
                </div>
            </CardHeader>

            <CardContent className="space-y-3">
                {extractedDebts.length === 0 ? (
                    <div className="text-center py-6 text-slate-500">
                        <FileText className="h-8 w-8 mx-auto mb-2 text-slate-400" />
                        <p>No debts found in the document.</p>
                        <p className="text-sm">Try uploading a clearer image.</p>
                    </div>
                ) : (
                    extractedDebts.map((debt, index) => (
                        <div
                            key={index}
                            className={cn(
                                "p-4 rounded-lg border transition-all",
                                addedDebts.has(index)
                                    ? "bg-progress-50 border-progress-200"
                                    : "bg-white border-slate-200 hover:border-main"
                            )}
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-semibold text-slate-900 truncate uppercase tracking-tight">
                                        {debt.creditor_name}
                                    </h4>
                                    <div className="flex flex-wrap gap-x-3 gap-y-1 mt-1">
                                        <span className="text-xs text-slate-500 font-medium">
                                            Balance: <span className="text-slate-900">{formatCurrency(debt.balance)}</span>
                                        </span>
                                        {debt.apr && (
                                            <span className="text-xs text-slate-500 font-medium">
                                                APR: <span className="text-slate-900">{debt.apr}%</span>
                                            </span>
                                        )}
                                        {debt.minimum_payment && (
                                            <span className="text-xs text-slate-500 font-medium">
                                                Min: <span className="text-slate-900">{formatCurrency(debt.minimum_payment)}</span>
                                            </span>
                                        )}
                                    </div>
                                </div>

                                <div className="flex items-center gap-2 ml-4">
                                    {onEditDebt && (
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => onEditDebt(debt, index)}
                                            className="h-8 w-8"
                                        >
                                            <Edit2 className="h-4 w-4" />
                                        </Button>
                                    )}
                                    {onAddDebt && !addedDebts.has(index) && (
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleAddDebt(debt, index)}
                                            leftIcon={<Plus className="h-4 w-4" />}
                                        >
                                            Add
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </CardContent>
        </Card>
    );
}
