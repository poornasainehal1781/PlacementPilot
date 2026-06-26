import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Briefcase, LogOut, LayoutDashboard, FileText, User, MessageSquare } from 'lucide-react';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    if (!user) return null;

    const isActive = (path) => location.pathname === path;
    const activeClass = "bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 shadow-md shadow-indigo-500/5";
    const inactiveClass = "text-slate-300 hover:bg-slate-800/30 hover:text-white border border-transparent";
    return (
        <div className="sticky top-0 z-50 w-full px-4 pt-4 pb-2 max-w-7xl mx-auto">
            <nav className="backdrop-blur-xl bg-slate-950/40 border border-slate-800/40 px-6 py-3.5 rounded-2xl shadow-2xl shadow-slate-950/60 flex items-center justify-between">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 text-xl font-bold tracking-tight text-white hover:opacity-90 transition-opacity">
                    <div className="bg-gradient-to-tr from-indigo-500 to-emerald-400 p-2 rounded-xl text-white shadow-lg shadow-indigo-500/20">
                        <Briefcase className="w-5 h-5" />
                    </div>
                    <span className="font-heading">TalentForge <span className="bg-gradient-to-r from-indigo-400 via-fuchsia-400 to-emerald-400 bg-clip-text text-transparent">AI</span></span>
                </Link>

                {/* Nav Links */}
                <div className="flex items-center gap-1.5">
                    <Link
                        to="/"
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${isActive('/') ? activeClass : inactiveClass}`}
                    >
                        <LayoutDashboard className="w-4 h-4" />
                        <span>Dashboard</span>
                    </Link>
                    <Link
                        to="/analyze"
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${isActive('/analyze') ? activeClass : inactiveClass}`}
                    >
                        <FileText className="w-4 h-4" />
                        <span>Analyze Resume</span>
                    </Link>
                    <Link
                        to="/chat"
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${isActive('/chat') ? activeClass : inactiveClass}`}
                    >
                        <MessageSquare className="w-4 h-4" />
                        <span>AI Chat Coach</span>
                    </Link>
                </div>

                {/* Profile / Logout */}
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 border-r border-slate-800 pr-4">
                        <div className="w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-300 font-semibold uppercase">
                            {user.username.charAt(0)}
                        </div>
                        <span className="text-sm font-medium text-slate-350 hidden md:block">
                            {user.username}
                        </span>
                    </div>

                    <button
                        onClick={() => {
                            logout();
                            navigate('/login');
                        }}
                        className="flex items-center gap-2 bg-slate-900/60 border border-slate-800 hover:border-red-500/30 hover:bg-red-500/10 text-slate-300 hover:text-red-400 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 cursor-pointer"
                    >
                        <LogOut className="w-4 h-4" />
                        <span className="hidden md:block">Logout</span>
                    </button>
                </div>
            </nav>
        </div>
    );
}
