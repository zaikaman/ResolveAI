import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import api from '../services/api';

export default function Onboarding() {
    const navigate = useNavigate();
    const { user } = useAuthStore();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [formData, setFormData] = useState({
        income: '',
        expenses: '',
        debtAllowance: '',
    });

    const [acceptedTerms, setAcceptedTerms] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        // Only allow numbers
        if (value && !/^\d*\.?\d*$/.test(value)) return;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user) return;
        if (!acceptedTerms) {
            setError('Please accept the terms and conditions');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // Server-only encryption: send plaintext, server encrypts before storage
            const payload = {
                monthly_income: formData.income,
                monthly_expenses: formData.expenses,
                available_for_debt: formData.debtAllowance,
                terms_accepted: true
            };

            const response = await api.post('/auth/onboarding/complete', payload);

            // Update user in store directly to ensure state is fresh before redirect
            const { setUser } = useAuthStore.getState();
            if (response.data) {
                setUser(response.data);
            }

            navigate('/dashboard');
        } catch (err: any) {
            console.error('Onboarding failed:', err);
            setError(err.message || 'Failed to complete setup. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 space-y-8">
                <div className="text-center space-y-2">
                    <h1 className="text-3xl font-bold text-slate-900">Welcome to Resolve AI</h1>
                    <p className="text-slate-500">Let's set up your financial profile to get started.</p>
                </div>

                {error && (
                    <div className="p-4 rounded-lg bg-red-50 text-red-600 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <Input
                        label="Monthly Income"
                        name="income"
                        value={formData.income}
                        onChange={handleChange}
                        placeholder="e.g. 5000"
                        required
                        leftIcon={<span className="text-slate-500">$</span>}
                        helperText="Your total monthly income after taxes"
                    />

                    <Input
                        label="Monthly Expenses"
                        name="expenses"
                        value={formData.expenses}
                        onChange={handleChange}
                        placeholder="e.g. 3000"
                        required
                        leftIcon={<span className="text-slate-500">$</span>}
                        helperText="Essential living expenses (rent, food, utilities)"
                    />

                    <Input
                        label="Debt Allowance"
                        name="debtAllowance"
                        value={formData.debtAllowance}
                        onChange={handleChange}
                        placeholder="e.g. 1000"
                        required
                        leftIcon={<span className="text-slate-500">$</span>}
                        helperText="How much can you afford to pay towards debt monthly?"
                    />

                    <div className="flex items-start gap-3 p-4 rounded-lg bg-slate-50 border border-slate-100">
                        <input
                            type="checkbox"
                            id="terms"
                            checked={acceptedTerms}
                            onChange={(e) => setAcceptedTerms(e.target.checked)}
                            className="mt-1 h-4 w-4 rounded border-slate-300 text-main focus:ring-main"
                        />
                        <label htmlFor="terms" className="text-sm text-slate-600 leading-tight cursor-pointer select-none">
                            I agree to the Terms of Service and Privacy Policy, and I understand that my financial data is encrypted securely.
                        </label>
                    </div>

                    <Button
                        type="submit"
                        className="w-full h-12 text-lg font-medium shadow-lg shadow-main/20 hover:shadow-main/30 transition-all"
                        isLoading={loading}
                        disabled={!acceptedTerms || !formData.income || !formData.expenses}
                    >
                        Complete Setup
                    </Button>
                </form>
            </div>
        </div>
    );
}
