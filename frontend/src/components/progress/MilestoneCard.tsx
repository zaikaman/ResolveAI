/**
 * MilestoneCard component - Celebration and achievement display
 */

import { useState, useEffect } from 'react';
import { 
    Trophy, 
    Star, 
    Flame, 
    Target, 
    Award, 
    Zap,
    PartyPopper,
    Medal,
    Crown
} from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { formatCurrency } from '../../utils/formatting';
import { cn } from '../../utils/cn';
import type { Milestone, MilestoneCheckResult } from '../../services/paymentService';

interface MilestoneCardProps {
    milestone: Milestone;
    compact?: boolean;
    onClick?: () => void;
}

interface CelebrationModalProps {
    isOpen: boolean;
    onClose: () => void;
    milestones: MilestoneCheckResult;
}

const badgeConfig: Record<string, { icon: typeof Trophy; color: string; bg: string }> = {
    first_victory: { icon: Star, color: 'text-yellow-500', bg: 'bg-yellow-100' },
    debt_destroyer: { icon: Trophy, color: 'text-amber-500', bg: 'bg-amber-100' },
    streak_starter: { icon: Flame, color: 'text-orange-500', bg: 'bg-orange-100' },
    week_warrior: { icon: Zap, color: 'text-blue-500', bg: 'bg-blue-100' },
    month_master: { icon: Medal, color: 'text-purple-500', bg: 'bg-purple-100' },
    quarter_champion: { icon: Crown, color: 'text-indigo-500', bg: 'bg-indigo-100' },
    halfway_hero: { icon: Target, color: 'text-green-500', bg: 'bg-green-100' },
    almost_there: { icon: PartyPopper, color: 'text-pink-500', bg: 'bg-pink-100' },
    debt_free: { icon: Crown, color: 'text-yellow-600', bg: 'bg-gradient-to-br from-yellow-100 to-amber-100' },
    negotiator: { icon: Award, color: 'text-teal-500', bg: 'bg-teal-100' },
    saver: { icon: Star, color: 'text-emerald-500', bg: 'bg-emerald-100' },
};

const milestoneTypeConfig: Record<string, { icon: typeof Trophy; color: string }> = {
    debt_paid_off: { icon: Trophy, color: 'text-amber-500' },
    percentage_milestone: { icon: Target, color: 'text-green-500' },
    consistency_streak: { icon: Flame, color: 'text-orange-500' },
    negotiation_success: { icon: Award, color: 'text-teal-500' },
    savings_milestone: { icon: Star, color: 'text-emerald-500' },
    first_payment: { icon: Star, color: 'text-yellow-500' },
    monthly_goal: { icon: Medal, color: 'text-purple-500' },
};

export function MilestoneCard({ milestone, compact = false, onClick }: MilestoneCardProps) {
    const badge = milestone.badge_name ? badgeConfig[milestone.badge_name] : null;
    const typeConfig = milestoneTypeConfig[milestone.milestone_type] || milestoneTypeConfig.percentage_milestone;
    const Icon = badge?.icon || typeConfig.icon;
    const iconColor = badge?.color || typeConfig.color;

    if (compact) {
        return (
            <div 
                onClick={onClick}
                className={cn(
                    "flex items-center gap-3 p-3 rounded-lg border border-slate-200 bg-white hover:shadow-sm transition-all cursor-pointer",
                    onClick && "hover:border-main"
                )}
            >
                <div className={cn("p-2 rounded-full", badge?.bg || 'bg-slate-100')}>
                    <Icon className={cn("h-4 w-4", iconColor)} />
                </div>
                <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-900 truncate text-sm">{milestone.title}</p>
                    <p className="text-xs text-slate-500 truncate">{milestone.description}</p>
                </div>
                {milestone.badge_name && (
                    <span className="px-2 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-700 rounded-full">
                        Badge
                    </span>
                )}
            </div>
        );
    }

    return (
        <div 
            onClick={onClick}
            className={cn(
                "p-4 rounded-xl border-2 border-yellow-200 bg-gradient-to-br from-yellow-50 to-amber-50",
                "hover:shadow-md transition-all",
                onClick && "cursor-pointer"
            )}
        >
            <div className="flex items-start gap-4">
                <div className={cn(
                    "p-3 rounded-full",
                    badge?.bg || 'bg-yellow-100'
                )}>
                    <Icon className={cn("h-6 w-6", iconColor)} />
                </div>
                <div className="flex-1">
                    <h3 className="font-bold text-slate-900 text-lg">{milestone.title}</h3>
                    <p className="text-slate-600 text-sm mt-1">{milestone.description}</p>
                    
                    {milestone.celebration_message && (
                        <p className="text-amber-700 font-medium mt-2 text-sm">
                            {milestone.celebration_message}
                        </p>
                    )}
                    
                    {milestone.interest_saved && milestone.interest_saved > 0 && (
                        <p className="text-green-600 text-sm mt-2">
                            💰 {formatCurrency(milestone.interest_saved)} saved!
                        </p>
                    )}
                    
                    {milestone.badge_name && (
                        <div className="mt-3 inline-flex items-center gap-1 px-3 py-1 bg-yellow-200 rounded-full">
                            <Award className="h-3 w-3 text-yellow-700" />
                            <span className="text-xs font-medium text-yellow-700">
                                {milestone.badge_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export function CelebrationModal({ isOpen, onClose, milestones }: CelebrationModalProps) {
    const [confettiActive, setConfettiActive] = useState(false);

    useEffect(() => {
        if (isOpen && milestones.celebration_priority >= 2) {
            setConfettiActive(true);
            const timer = setTimeout(() => setConfettiActive(false), 3000);
            return () => clearTimeout(timer);
        }
    }, [isOpen, milestones]);

    if (!milestones.has_new_milestones || milestones.milestones.length === 0) {
        return null;
    }

    const primaryMilestone = milestones.milestones[0];
    const additionalMilestones = milestones.milestones.slice(1);

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            size="md"
        >
            <div className="text-center py-4">
                {/* Confetti animation placeholder */}
                {confettiActive && (
                    <div className="absolute inset-0 pointer-events-none overflow-hidden">
                        {[...Array(20)].map((_, i) => (
                            <div
                                key={i}
                                className="absolute animate-bounce"
                                style={{
                                    left: `${Math.random() * 100}%`,
                                    top: `${Math.random() * 50}%`,
                                    animationDelay: `${Math.random() * 0.5}s`,
                                    animationDuration: `${0.5 + Math.random() * 0.5}s`
                                }}
                            >
                                {['🎉', '🎊', '⭐', '✨', '🏆'][Math.floor(Math.random() * 5)]}
                            </div>
                        ))}
                    </div>
                )}

                {/* Trophy icon */}
                <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-yellow-100 to-amber-100 flex items-center justify-center">
                    <Trophy className="h-10 w-10 text-yellow-500" />
                </div>

                {/* Celebration header */}
                <h2 className="text-2xl font-bold text-slate-900 mb-2">
                    🎉 Congratulations! 🎉
                </h2>
                <p className="text-slate-600 mb-6">
                    You've achieved something amazing!
                </p>

                {/* Primary milestone */}
                <div className="mb-6">
                    <MilestoneCard milestone={primaryMilestone} />
                </div>

                {/* Additional milestones */}
                {additionalMilestones.length > 0 && (
                    <div className="space-y-2 mb-6">
                        <p className="text-sm font-medium text-slate-500 mb-2">
                            And more achievements!
                        </p>
                        {additionalMilestones.map((milestone, index) => (
                            <MilestoneCard 
                                key={index} 
                                milestone={milestone} 
                                compact 
                            />
                        ))}
                    </div>
                )}

                {/* Action button */}
                <Button onClick={onClose} className="w-full">
                    Keep Going! 🚀
                </Button>
            </div>
        </Modal>
    );
}

export function AchievementBadge({ 
    badgeName, 
    unlocked = true,
    size = 'md'
}: { 
    badgeName: string; 
    unlocked?: boolean;
    size?: 'sm' | 'md' | 'lg';
}) {
    const config = badgeConfig[badgeName] || { icon: Award, color: 'text-slate-400', bg: 'bg-slate-100' };
    const Icon = config.icon;

    const sizeConfig = {
        sm: { container: 'w-10 h-10', icon: 'h-4 w-4' },
        md: { container: 'w-14 h-14', icon: 'h-6 w-6' },
        lg: { container: 'w-20 h-20', icon: 'h-8 w-8' },
    };

    return (
        <div className="flex flex-col items-center gap-1">
            <div className={cn(
                "rounded-full flex items-center justify-center transition-all",
                sizeConfig[size].container,
                unlocked ? config.bg : 'bg-slate-100',
                !unlocked && 'opacity-50 grayscale'
            )}>
                <Icon className={cn(
                    sizeConfig[size].icon,
                    unlocked ? config.color : 'text-slate-300'
                )} />
            </div>
            <span className={cn(
                "text-xs font-medium text-center",
                unlocked ? 'text-slate-700' : 'text-slate-400'
            )}>
                {badgeName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </span>
        </div>
    );
}

export default MilestoneCard;
