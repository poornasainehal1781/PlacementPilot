import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Briefcase, User, Mail, Lock, UserPlus, AlertCircle, CheckCircle2, Eye, EyeOff } from 'lucide-react';
import Card from '../components/Card';

export default function Register() {
    const { register } = useAuth();
    const navigate = useNavigate();

    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(false);

        if (!username || !email || !password || !confirmPassword) {
            setError("All fields are required.");
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        if (password.length < 6) {
            setError("Password must be at least 6 characters.");
            return;
        }

        setLoading(true);
        const result = await register(username, email, password);
        setLoading(false);

        if (result.success) {
            setSuccess(true);
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } else {
            setError(result.error);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="w-full max-w-md relative">
                {/* Visual Ambient Glow Orbs */}
                <div className="absolute -top-12 -left-12 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
                <div className="absolute -bottom-12 -right-12 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

                {/* Logo / Header */}
                <div className="flex flex-col items-center mb-8 relative z-10 animate-fade-in">
                    <div className="bg-gradient-to-tr from-indigo-500 to-emerald-400 p-3 rounded-2xl text-white shadow-xl shadow-indigo-500/20 mb-4 transform hover:scale-105 transition-transform duration-300">
                        <Briefcase className="w-8 h-8" />
                    </div>
                    <h2 className="text-3xl font-extrabold text-white tracking-tight font-heading">
                        Create Account
                    </h2>
                    <p className="text-slate-400 text-sm mt-1">
                        Start optimizing your resume for ATS
                    </p>
                </div>

                {/* Form Card */}
                <Card className="p-8 backdrop-blur-xl bg-slate-950/40 border border-slate-800/40 shadow-2xl shadow-indigo-500/5 relative z-10 animate-fade-in">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm">
                                <AlertCircle className="w-5 h-5 shrink-0" />
                                <span>{error}</span>
                            </div>
                        )}

                        {success && (
                            <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-4 rounded-xl text-sm">
                                <CheckCircle2 className="w-5 h-5 shrink-0" />
                                <span>Account created successfully! Redirecting...</span>
                            </div>
                        )}

                        <div className="space-y-1.5">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Username
                            </label>
                            <div className="relative">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="yourname"
                                    className="w-full bg-slate-950/80 border border-slate-800/80 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3.5 pl-12 pr-4 text-slate-200 placeholder-slate-600 outline-none transition-all duration-300"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Email Address
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="name@example.com"
                                    className="w-full bg-slate-950/80 border border-slate-800/80 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3.5 pl-12 pr-4 text-slate-200 placeholder-slate-600 outline-none transition-all duration-300"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="•••••••• (Min 6 chars)"
                                    className="w-full bg-slate-950/80 border border-slate-800/80 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3.5 pl-12 pr-12 text-slate-200 placeholder-slate-600 outline-none transition-all duration-300"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Confirm Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type={showConfirmPassword ? "text" : "password"}
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full bg-slate-950/80 border border-slate-800/80 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3.5 pl-12 pr-12 text-slate-200 placeholder-slate-600 outline-none transition-all duration-300"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading || success}
                            className="w-full bg-gradient-to-r from-indigo-500 to-emerald-500 hover:from-indigo-600 hover:to-emerald-600 text-white font-semibold py-3.5 rounded-xl transition-all duration-300 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/35 transform hover:-translate-y-0.5 cursor-pointer flex items-center justify-center gap-2"
                        >
                            <UserPlus className="w-4 h-4" />
                            {loading ? "Creating account..." : "Create Account"}
                        </button>
                    </form>
                </Card>

                {/* Footer link */}
                <p className="text-center text-slate-400 text-sm mt-6 relative z-10">
                    Already have an account?{' '}
                    <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    );
}
