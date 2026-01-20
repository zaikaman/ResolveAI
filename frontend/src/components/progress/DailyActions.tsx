/**
 * DailyActions component - Display prioritized daily actions
 */

import { 
    CheckCircle, 
    Clock, 
    AlertTriangle, 
    Target, 
    Sparkles,
    ChevronRight,
    DollarSign,
    Eye
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Button } from '../common/Button';
import { cn } from '../../utils/cn';
import { formatCurrency } from '../../utils/formatting';
import type { DailyAction, DailyActionsResponse } from '../../services/paymentService';

interface DailyActionsProps {
    actionsData: DailyActionsResponse | null;
    loading?: boolean;
    onPayAction?: (action: DailyAction) => void;
    onViewAction?: (action: DailyAction) => void;
}

const priorityConfig = {
    1: { label: 'Urgent', color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' },
    2: { label: 'High', color: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200' },
    3: { label: 'Medium', color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200' },
    4: { label: 'Low', color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' },
    5: { label: 'Optional', color: 'text-slate-500', bg: 'bg-slate-50', border: 'border-slate-200' },
};

const actionTypeConfig = {
    payment: { icon: DollarSign, label: 'Payment', color: 'text-green-600' },
    review: { icon: Eye, label: 'Review', color: 'text-blue-600' },
    rest: { icon: Sparkles, label: 'Rest Day', color: 'text-purple-600' },
    milestone: { icon: Target, label: 'Milestone', color: 'text-yellow-600' },
    nudge: { icon: AlertTriangle, label: 'Reminder', color: 'text-orange-600' },
};

function ActionCard({ 
    action, 
    onPay, 
    onView 
}: { 
    action: DailyAction; 
    onPay?: () => void;
    onView?: () => void;
}) {
    const priority = priorityConfig[action.priority] || priorityConfig[3];
    const actionType = actionTypeConfig[action.action_type] || actionTypeConfig.review;
    const Icon = actionType.icon;

    return (
        <div 
            className={cn(
                "p-4 rounded-lg border transition-all hover:shadow-sm",
                priority.bg,
                priority.border,
                action.is_overdue && "ring-2 ring-red-300"
            )}
        >
            <div className="flex items-start gap-3">
                <div className={cn("p-2 rounded-lg bg-white", actionType.color)}>
                    <Icon className="h-5 w-5" />
                </div>
                
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-slate-900 truncate">
                            {action.title}
                        </h4>
                        {action.is_overdue && (
                            <span className="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-700 rounded-full">
                                Overdue
                            </span>
                        )}
                        <span className={cn("px-2 py-0.5 text-xs font-medium rounded-full", priority.color, priority.bg)}>
                            {priority.label}
                        </span>
                    </div>
                    
                    <p className="text-sm text-slate-600 mb-2">
                        {action.description}
                    </p>
                    
                    {action.motivational_message && (
                        <p className="text-sm text-slate-500 italic mb-3">
                            {action.motivational_message}
                        </p>
                    )}
                    
                    <div className="flex items-center gap-2">
                        {action.action_type === 'payment' && action.suggested_amount && onPay && (
                            <Button 
                                size="sm" 
                                onClick={onPay}
                                leftIcon={<DollarSign className="h-4 w-4" />}
                            >
                                Pay {formatCurrency(action.suggested_amount)}
                            </Button>
                        )}
                        
                        {action.action_type === 'review' && onView && (
                            <Button 
                                size="sm" 
                                variant="secondary"
                                onClick={onView}
                                rightIcon={<ChevronRight className="h-4 w-4" />}
                            >
                                View
                            </Button>
                        )}
                        
                        {action.due_date && (
                            <span className="text-xs text-slate-500 flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                Due {new Date(action.due_date).toLocaleDateString()}
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export function DailyActions({ 
    actionsData, 
    loading = false,
    onPayAction,
    onViewAction
}: DailyActionsProps) {
    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5 text-main" />
                        Today's Actions
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-24 bg-slate-100 rounded-lg animate-pulse" />
                        ))}
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (!actionsData || actionsData.actions.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5 text-main" />
                        Today's Actions
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8">
                        <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
                        <h3 className="text-lg font-semibold text-slate-900 mb-1">
                            All caught up!
                        </h3>
                        <p className="text-slate-500">
                            No actions needed today. Enjoy your rest day!
                        </p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5 text-main" />
                        Today's Actions
                    </CardTitle>
                    {actionsData.streak_message && (
                        <span className="text-sm font-medium text-orange-600">
                            {actionsData.streak_message}
                        </span>
                    )}
                </div>
                <p className="text-sm text-slate-500 mt-1">
                    {actionsData.summary}
                </p>
            </CardHeader>
            <CardContent>
                <div className="space-y-3">
                    {actionsData.actions.map((action, index) => (
                        <ActionCard
                            key={`${action.action_type}-${action.debt_id || index}`}
                            action={action}
                            onPay={onPayAction ? () => onPayAction(action) : undefined}
                            onView={onViewAction ? () => onViewAction(action) : undefined}
                        />
                    ))}
                </div>
                
                {actionsData.progress_message && (
                    <div className="mt-4 p-3 bg-main/5 rounded-lg border border-main/20">
                        <p className="text-sm text-main font-medium">
                            {actionsData.progress_message}
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

export default DailyActions;
