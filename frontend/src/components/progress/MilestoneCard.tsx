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

const badgeConfig: Record<string, { icon: typeof Trophy; color: string; bg: string; gradient: string }> = {
    first_victory: { icon: Star, color: 'text-yellow-100', bg: 'bg-yellow-900', gradient: 'from-yellow-400 to-amber-600' },
    debt_destroyer: { icon: Trophy, color: 'text-amber-100', bg: 'bg-amber-900', gradient: 'from-amber-400 to-orange-600' },
    streak_starter: { icon: Flame, color: 'text-orange-100', bg: 'bg-orange-900', gradient: 'from-orange-400 to-red-600' },
    week_warrior: { icon: Zap, color: 'text-blue-100', bg: 'bg-blue-900', gradient: 'from-blue-400 to-indigo-600' },
    month_master: { icon: Medal, color: 'text-purple-100', bg: 'bg-purple-900', gradient: 'from-purple-400 to-violet-600' },
    quarter_champion: { icon: Crown, color: 'text-indigo-100', bg: 'bg-indigo-900', gradient: 'from-indigo-400 to-purple-600' },
    halfway_hero: { icon: Target, color: 'text-emerald-100', bg: 'bg-emerald-900', gradient: 'from-emerald-400 to-teal-600' },
    almost_there: { icon: PartyPopper, color: 'text-pink-100', bg: 'bg-pink-900', gradient: 'from-pink-400 to-rose-600' },
    debt_free: { icon: Crown, color: 'text-yellow-100', bg: 'bg-yellow-900', gradient: 'from-yellow-300 via-amber-400 to-yellow-500' },
    negotiator: { icon: Award, color: 'text-teal-100', bg: 'bg-teal-900', gradient: 'from-teal-400 to-emerald-600' },
    saver: { icon: Star, color: 'text-emerald-100', bg: 'bg-emerald-900', gradient: 'from-emerald-400 to-green-600' },
};

const milestoneTypeConfig: Record<string, { icon: typeof Trophy; color: string; gradient: string }> = {
    debt_paid_off: { icon: Trophy, color: 'text-amber-600', gradient: 'from-amber-400 to-orange-500' },
    percentage_milestone: { icon: Target, color: 'text-green-600', gradient: 'from-green-400 to-emerald-500' },
    consistency_streak: { icon: Flame, color: 'text-orange-600', gradient: 'from-orange-400 to-red-500' },
    negotiation_success: { icon: Award, color: 'text-teal-600', gradient: 'from-teal-400 to-cyan-500' },
    savings_milestone: { icon: Star, color: 'text-emerald-600', gradient: 'from-emerald-400 to-green-500' },
    first_payment: { icon: Star, color: 'text-yellow-600', gradient: 'from-yellow-400 to-amber-500' },
    monthly_goal: { icon: Medal, color: 'text-purple-600', gradient: 'from-purple-400 to-indigo-500' },
};

export function MilestoneCard({ milestone, compact = false, onClick }: MilestoneCardProps) {
    const badge = milestone.badge_name ? badgeConfig[milestone.badge_name] : null;
    const typeConfig = milestoneTypeConfig[milestone.milestone_type] || milestoneTypeConfig.percentage_milestone;
    const Icon = badge?.icon || typeConfig.icon;

    // Compact View (List Items)
    if (compact) {
        // Use simpler colors for compact view to avoid visual noise
        const simpleColor = badge ? 'text-amber-600 bg-amber-100' : 'text-slate-600 bg-slate-100';

        return (
            <div
                onClick={onClick}
                className={cn(
                    "group flex items-center gap-4 p-4 rounded-xl border border-slate-100 bg-white hover:border-slate-200 hover:shadow-md transition-all duration-300 cursor-pointer",
                    onClick && "hover:-translate-y-0.5"
                )}
            >
                <div className={cn("p-2.5 rounded-full transition-colors", simpleColor)}>
                    <Icon className="h-5 w-5" />
                </div>
                <div className="flex-1 min-w-0">
                    <p className="font-semibold text-slate-900 truncate">{milestone.title}</p>
                    <p className="text-sm text-slate-500 truncate">{milestone.description}</p>
                </div>
                {milestone.badge_name && (
                    <span className="px-2.5 py-1 text-xs font-semibold bg-amber-50 text-amber-700 rounded-full border border-amber-100">
                        Badge
                    </span>
                )}
            </div>
        );
    }

    // Featured View (Modal Centerpiece)
    const gradientClass = badge?.gradient || typeConfig.gradient;

    return (
        <div
            onClick={onClick}
            className={cn(
                "relative p-8 rounded-2xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50",
                "flex flex-col items-center text-center",
                "transition-all duration-500 animate-in fade-in zoom-in-95 slide-in-from-bottom-2",
                onClick && "cursor-pointer hover:shadow-2xl hover:-translate-y-1"
            )}
        >
            {/* Glow effect slightly behind the icon */}
            <div className={cn(
                "absolute top-8 left-1/2 -translate-x-1/2 w-24 h-24 rounded-full opacity-20 blur-2xl",
                "bg-gradient-to-tr", gradientClass
            )} />

            {/* Icon Circle */}
            <div className={cn(
                "relative relative w-20 h-20 rounded-2xl rotate-3 mb-6 flex items-center justify-center shadow-lg",
                "bg-gradient-to-br text-white", gradientClass
            )}>
                <Icon className="h-10 w-10 drop-shadow-md" />

                {/* Shine effect */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-transparent via-white/20 to-transparent" />
            </div>

            {/* Content */}
            <div className="space-y-3 max-w-sm">
                <h3 className="text-2xl font-bold text-slate-900 tracking-tight leading-tight">
                    {milestone.title}
                </h3>

                <p className="text-slate-600 leading-relaxed">
                    {milestone.description}
                </p>

                {milestone.celebration_message && (
                    <div className="pt-2">
                        <p className={cn(
                            "inline-block px-4 py-1.5 rounded-full text-sm font-medium",
                            "bg-gradient-to-r from-amber-50 to-orange-50 text-amber-800 border border-amber-100"
                        )}>
                            ✨ {milestone.celebration_message}
                        </p>
                    </div>
                )}

                {milestone.interest_saved && milestone.interest_saved > 0 && (
                    <p className="text-emerald-600 font-semibold text-lg pt-1">
                        Saved {formatCurrency(milestone.interest_saved)} in interest!
                    </p>
                )}
            </div>

            {/* Badge Indicator if applicable */}
            {milestone.badge_name && (
                <div className="mt-6 pt-6 border-t border-slate-100 w-full flex justify-center">
                    <div className="flex items-center gap-2 text-sm text-slate-500">
                        <Award className="h-4 w-4 text-amber-500" />
                        <span>Badge Unlocked:</span>
                        <span className="font-semibold text-slate-900">
                            {milestone.badge_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}

export function CelebrationModal({ isOpen, onClose, milestones }: CelebrationModalProps) {
    const [confettiActive, setConfettiActive] = useState(false);

    useEffect(() => {
        if (isOpen && milestones.celebration_priority >= 2) {
            setConfettiActive(true);
            const timer = setTimeout(() => setConfettiActive(false), 4000);
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
            size="lg" // Larger modal for the premium feel
            hideCloseButton // We'll add a custom close/action button
        >
            <div className="relative py-8 px-4 flex flex-col items-center">
                {/* Background decorations */}
                <div className="absolute inset-0 bg-gradient-to-b from-slate-50/50 to-white -z-10" />

                {/* Confetti */}
                {confettiActive && (
                    <div className="absolute inset-0 pointer-events-none overflow-hidden z-50">
                        {[...Array(40)].map((_, i) => (
                            <div
                                key={i}
                                className="absolute animate-[fall_3s_ease-in-out_infinite]"
                                style={{
                                    left: `${Math.random() * 100}%`,
                                    top: `-${Math.random() * 20}%`,
                                    animationDelay: `${Math.random() * 2}s`,
                                    transform: `rotate(${Math.random() * 360}deg)`,
                                    fontSize: `${0.8 + Math.random() * 0.8}rem`
                                }}
                            >
                                {['🎉', '✨', '🎊', '⭐️', '🔶', '🔷'][Math.floor(Math.random() * 6)]}
                            </div>
                        ))}
                    </div>
                )}

                {/* Header Section */}
                <div className="text-center mb-10 space-y-2 relative">
                    <div className="inline-flex items-center justify-center p-3 bg-yellow-100 rounded-full mb-4 ring-8 ring-yellow-50 animate-bounce">
                        <Trophy className="h-8 w-8 text-yellow-600" />
                    </div>
                    <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                        Congratulations!
                    </h2>
                    <p className="text-lg text-slate-500 font-medium">
                        You've just hit a major milestone
                    </p>
                </div>

                {/* Main Content */}
                <div className="w-full max-w-md relative z-10 mb-8">
                    <MilestoneCard milestone={primaryMilestone} />
                </div>

                {/* Additional Achievements */}
                {additionalMilestones.length > 0 && (
                    <div className="w-full max-w-md mb-8 space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300 fill-mode-both">
                        <div className="flex items-center gap-4 text-sm text-slate-400 mb-2">
                            <div className="h-px bg-slate-200 flex-1" />
                            <span>Also Unlocked</span>
                            <div className="h-px bg-slate-200 flex-1" />
                        </div>
                        {additionalMilestones.map((milestone, index) => (
                            <MilestoneCard
                                key={index}
                                milestone={milestone}
                                compact
                            />
                        ))}
                    </div>
                )}

                {/* Action Button */}
                <div className="w-full max-w-xs">
                    <Button
                        onClick={onClose}
                        className="w-full h-12 text-lg shadow-lg shadow-main/25 hover:shadow-xl hover:shadow-main/30 hover:-translate-y-0.5 transition-all duration-300"
                    >
                        Keep up the momentum! 🚀
                    </Button>
                </div>
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
    const config = badgeConfig[badgeName] || { icon: Award, color: 'text-slate-400', bg: 'bg-slate-100', gradient: 'gray' };
    const Icon = config.icon;

    const sizeConfig = {
        sm: { container: 'w-10 h-10', icon: 'h-4 w-4' },
        md: { container: 'w-14 h-14', icon: 'h-6 w-6' },
        lg: { container: 'w-20 h-20', icon: 'h-8 w-8' },
    };

    return (
        <div className="flex flex-col items-center gap-2 group">
            <div className={cn(
                "rounded-full flex items-center justify-center transition-all duration-500",
                "bg-gradient-to-br shadow-sm",
                sizeConfig[size].container,
                unlocked
                    ? cn(config.gradient, "text-white shadow-md group-hover:shadow-lg group-hover:scale-110")
                    : "from-slate-100 to-slate-200 text-slate-400 grayscale"
            )}>
                <Icon className={cn(sizeConfig[size].icon, "drop-shadow-sm")} />
            </div>
            <span className={cn(
                "text-xs font-medium text-center transition-colors",
                unlocked ? 'text-slate-700 group-hover:text-slate-900' : 'text-slate-400'
            )}>
                {badgeName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </span>
        </div>
    );
}
export default MilestoneCard;
