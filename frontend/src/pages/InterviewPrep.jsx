import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Sparkles, BookOpen, CheckCircle, HelpCircle, Eye, EyeOff, ShieldAlert, MessageSquare } from 'lucide-react';
import Card from '../components/Card';

export default function InterviewPrep() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Track revealed state for each question index
    const [revealed, setRevealed] = useState({});
    // Track checklist status for each question ID: 'mastered' or 'pending'
    const [statuses, setStatuses] = useState({});

    useEffect(() => {
        fetchResult();
    }, [id]);

    const fetchResult = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`/analysis/${id}`);
            setData(response.data);
            
            // Load saved question mastery statuses from localStorage
            const savedStatuses = localStorage.getItem(`prep_status_${id}`);
            if (savedStatuses) {
                setStatuses(JSON.parse(savedStatuses));
            }
        } catch (err) {
            console.error('Error fetching prep questions:', err);
            setError('Failed to load interview prep questions.');
        } finally {
            setLoading(false);
        }
    };

    const toggleReveal = (idx) => {
        setRevealed(prev => ({
            ...prev,
            [idx]: !prev[idx]
        }));
    };

    const toggleStatus = (qId) => {
        const current = statuses[qId] || 'pending';
        const updated = {
            ...statuses,
            [qId]: current === 'mastered' ? 'pending' : 'mastered'
        };
        setStatuses(updated);
        localStorage.setItem(`prep_status_${id}`, JSON.stringify(updated));
    };

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-12 flex items-center justify-center min-h-[60vh]">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-slate-400 font-medium">Generating custom prep cards...</p>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-12">
                <Card className="border-red-500/20 bg-red-500/5 p-8 flex flex-col items-center text-center">
                    <ShieldAlert className="w-12 h-12 text-red-400 mb-3" />
                    <h3 className="text-xl font-bold text-slate-200">Prep Dashboard Unavailable</h3>
                    <p className="text-slate-400 text-sm mt-1 mb-6">
                        We could not load interview questions.
                    </p>
                    <button 
                        onClick={() => navigate('/')}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-xl font-semibold text-sm transition-all"
                    >
                        Back to Dashboard
                    </button>
                </Card>
            </div>
        );
    }

    const { questions = [], job_description = {} } = data;
    const masteredCount = Object.values(statuses).filter(s => s === 'mastered').length;
    const progressPercent = questions.length > 0 ? Math.round((masteredCount / questions.length) * 100) : 0;

    return (
        <div className="max-w-4xl mx-auto px-6 py-10 space-y-8 animate-fade-in">
            {/* Header section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800/60 pb-6">
                <div>
                    <button
                        onClick={() => navigate(`/analysis/${id}`)}
                        className="flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors mb-3"
                    >
                        <ArrowLeft className="w-3.5 h-3.5" />
                        <span>Back to Analysis Audit</span>
                    </button>
                    <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
                        <Sparkles className="w-6 h-6 text-indigo-400" />
                        <span>Interview Prep: {job_description.title}</span>
                    </h1>
                    <p className="text-slate-400 text-xs md:text-sm mt-1">
                        Tailored practice based on your resume and matched criteria.
                    </p>
                </div>
                <button
                    onClick={() => navigate(`/chat/${id}`)}
                    className="bg-indigo-650 hover:bg-indigo-600 text-white font-semibold text-xs px-5 py-3.5 rounded-xl transition-all shadow-lg shadow-indigo-600/10 flex items-center gap-2 shrink-0 self-stretch sm:self-auto"
                >
                    <MessageSquare className="w-4 h-4" />
                    <span>Practice with AI Chatbot</span>
                </button>
            </div>

            {/* Progress summary Card */}
            {questions.length > 0 && (
                <Card hover={false} className="p-6">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
                        <div>
                            <h4 className="text-sm font-bold text-slate-200">Practice Progress</h4>
                            <p className="text-xs text-slate-400 mt-0.5">Master questions by reviewing strategy suggestions.</p>
                        </div>
                        <span className="text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-3 py-1.5 rounded-full border border-indigo-500/20">
                            {masteredCount} of {questions.length} Completed
                        </span>
                    </div>

                    <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-850">
                        <div 
                            className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 transition-all duration-500 ease-out"
                            style={{ width: `${progressPercent}%` }}
                        />
                    </div>
                </Card>
            )}

            {/* Questions list */}
            {questions.length === 0 ? (
                <Card className="text-center py-10">
                    <HelpCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                    <p className="text-sm text-slate-400">No custom interview questions generated for this profile.</p>
                </Card>
            ) : (
                <div className="space-y-6">
                    {questions.map((q, idx) => {
                        const isRevealed = !!revealed[idx];
                        const isMastered = statuses[q.id] === 'mastered';
                        const typeTagColor = q.question_type.includes("Behavioral")
                            ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
                            : q.question_type.includes("Preparation")
                            ? "text-amber-400 bg-amber-500/10 border-amber-500/20"
                            : "text-indigo-400 bg-indigo-500/10 border-indigo-500/20";

                        return (
                            <Card 
                                key={q.id} 
                                hover={false}
                                className={`border transition-all duration-300 ${
                                    isMastered ? 'border-emerald-500/20 bg-slate-900/40' : 'border-slate-800'
                                }`}
                            >
                                <div className="flex justify-between items-start gap-4 mb-4">
                                    <div className="flex flex-wrap gap-2 items-center">
                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-950 px-2.5 py-1 rounded-md border border-slate-850">
                                            Q{idx + 1}
                                        </span>
                                        <span className={`text-[10px] font-bold px-2.5 py-1 rounded-md border ${typeTagColor}`}>
                                            {q.question_type}
                                        </span>
                                    </div>

                                    {/* Mastery Checkbox */}
                                    <button
                                        onClick={() => toggleStatus(q.id)}
                                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                                            isMastered
                                                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                                                : 'bg-slate-950 text-slate-400 border-slate-850 hover:border-slate-700 hover:text-slate-350'
                                        }`}
                                    >
                                        <CheckCircle className={`w-3.5 h-3.5 ${isMastered ? 'fill-emerald-500/20' : ''}`} />
                                        <span>{isMastered ? 'Mastered' : 'Mark Mastered'}</span>
                                    </button>
                                </div>

                                <h3 className="text-base font-bold text-slate-100 leading-snug mb-5">
                                    {q.question}
                                </h3>

                                <div className="space-y-4">
                                    {/* Trigger reveal button */}
                                    <button
                                        onClick={() => toggleReveal(idx)}
                                        className="flex items-center gap-2 text-xs font-bold text-indigo-400 hover:text-indigo-350 transition-colors"
                                    >
                                        {isRevealed ? (
                                            <>
                                                <EyeOff className="w-4 h-4" />
                                                <span>Hide Answer Strategy</span>
                                            </>
                                        ) : (
                                            <>
                                                <Eye className="w-4 h-4" />
                                                <span>Reveal Answer Strategy</span>
                                            </>
                                        )}
                                    </button>

                                    {/* Answer guidelines section */}
                                    {isRevealed && (
                                        <div className="bg-slate-950/60 border border-slate-850 p-4 rounded-xl text-xs text-slate-350 leading-relaxed space-y-2 animate-fade-in">
                                            <p className="font-bold text-indigo-400 flex items-center gap-1">
                                                <BookOpen className="w-3.5 h-3.5" />
                                                <span>Suggested Response Strategy:</span>
                                            </p>
                                            <p>{q.answer_guideline}</p>
                                        </div>
                                    )}
                                </div>
                            </Card>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
