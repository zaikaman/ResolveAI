import { useAuth } from '../hooks/useAuth';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Sparkles, TrendingDown, Target, ArrowRight } from 'lucide-react';
import { Button } from '../components/common/Button';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="space-y-8">
            {/* Welcome Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">
                        Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!
                    </h1>
                    <p className="text-slate-500 mt-1">
                        Here's an overview of your debt freedom progress.
                    </p>
                </div>
                <Button onClick={() => navigate('/debts')}>Manage Debts</Button>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="bg-gradient-to-br from-main to-blue-700 text-white border-none">
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-white/10 rounded-lg">
                                <Target className="h-6 w-6 text-white" />
                            </div>
                            <h3 className="font-semibold text-blue-100">Next Milestone</h3>
                        </div>
                        <p className="text-2xl font-bold mb-1">Pay off Credit Card</p>
                        <p className="text-sm text-blue-200">on track for next month</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-green-100 rounded-lg">
                                <TrendingDown className="h-6 w-6 text-green-600" />
                            </div>
                            <h3 className="font-semibold text-slate-600">Total Progress</h3>
                        </div>
                        <p className="text-2xl font-bold text-slate-900">0%</p>
                        <p className="text-sm text-slate-500">Debt paid off so far</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-purple-100 rounded-lg">
                                <Sparkles className="h-6 w-6 text-purple-600" />
                            </div>
                            <h3 className="font-semibold text-slate-600">Streak</h3>
                        </div>
                        <p className="text-2xl font-bold text-slate-900">1 Day</p>
                        <p className="text-sm text-slate-500">Keep it up!</p>
                    </CardContent>
                </Card>
            </div>

            {/* Getting Started Section */}
            <div>
                <h2 className="text-xl font-bold text-slate-900 mb-4">Get Started</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card hoverable onClick={() => navigate('/debts')} className="cursor-pointer group">
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                1. Add Your Debts
                                <ArrowRight className="h-5 w-5 text-slate-400 group-hover:text-main transition-colors" />
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-slate-500">
                                List all your current debts or scan your statements to get a clear picture of what you owe.
                            </p>
                        </CardContent>
                    </Card>

                    <Card hoverable onClick={() => navigate('/plan')} className="cursor-pointer group">
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                2. Create Your Plan
                                <ArrowRight className="h-5 w-5 text-slate-400 group-hover:text-main transition-colors" />
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-slate-500">
                                Generate a personalized repayment strategy to become debt-free faster and save on interest.
                            </p>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
