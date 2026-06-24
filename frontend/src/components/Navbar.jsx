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
    const activeClass = "bg-indigo-600/30 text-indigo-400 border border-indigo-500/30";
    const inactiveClass = "text-slate-300 hover:bg-slate-800/50 hover:text-white border border-transparent";

    return (
        <nav className="sticky top-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800/80 px-6 py-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 text-xl font-bold tracking-tight text-white">
                    <div className="bg-gradient-to-tr from-indigo-600 to-emerald-500 p-2 rounded-xl text-white shadow-lg shadow-indigo-500/20">
                        <Briefcase className="w-5 h-5" />
                    </div>
                    <span>TalentForge <span className="bg-gradient-to-r from-indigo-400 to-emerald-400 bg-clip-text text-transparent">AI</span></span>
                </Link>

                {/* Nav Links */}
                <div className="flex items-center gap-2">
                    <Link
                        to="/"
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${isActive('/') ? activeClass : inactiveClass}`}
                    >
                        <LayoutDashboard className="w-4 h-4" />
                        <span>Dashboard</span>
                    </Link>
                    <Link
                        to="/analyze"
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${isActive('/analyze') ? activeClass : inactiveClass}`}
                    >
                        <FileText className="w-4 h-4" />
                        <span>Analyze Resume</span>
                    </Link>
                    <Link
                        to="/chat"
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${isActive('/chat') ? activeClass : inactiveClass}`}
                    >
                        <MessageSquare className="w-4 h-4" />
                        <span>AI Chat Coach</span>
                    </Link>
                </div>

                {/* Profile / Logout */}
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 border-r border-slate-800 pr-4">
                        <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-semibold uppercase">
                            {user.username.charAt(0)}
                        </div>
                        <span className="text-sm font-medium text-slate-300 hidden md:block">
                            {user.username}
                        </span>
                    </div>

                    <button
                        onClick={() => {
                            logout();
                            navigate('/login');
                        }}
                        className="flex items-center gap-2 bg-slate-900 border border-slate-800 hover:border-red-500/30 hover:bg-red-500/10 text-slate-300 hover:text-red-400 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200"
                    >
                        <LogOut className="w-4 h-4" />
                        <span className="hidden md:block">Logout</span>
                    </button>
                </div>
            </div>
        </nav>
    );
}
