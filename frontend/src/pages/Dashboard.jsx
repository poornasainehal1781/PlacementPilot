import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar, Cell } from 'recharts';
import { FileText, Cpu, CheckCircle2, TrendingUp, AlertCircle, Calendar, ArrowRight, Award } from 'lucide-react';
import Card from '../components/Card';

export default function Dashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const [statsRes, historyRes] = await Promise.all([
                axios.get('/dashboard/stats'),
                axios.get('/analysis/history')
            ]);
            setStats(statsRes.data);
            setHistory(historyRes.data);
        } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setError('Could not connect to the backend server. Make sure Flask is running.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-12 flex items-center justify-center min-h-[60vh]">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-slate-400 font-medium">Analyzing dashboard metrics...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-12">
                <Card className="border-red-500/20 bg-red-500/5 p-8 flex flex-col items-center text-center">
                    <AlertCircle className="w-12 h-12 text-red-400 mb-3" />
                    <h3 className="text-xl font-bold text-slate-200">Database Connection Failed</h3>
                    <p className="text-slate-400 text-sm max-w-md mt-1 mb-6">
                        {error}
                    </p>
                    <button 
                        onClick={fetchDashboardData}
                        className="bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-200 px-6 py-2.5 rounded-xl font-semibold text-sm transition-all"
                    >
                        Retry Connection
                    </button>
                </Card>
            </div>
        );
    }

    const {
        total_resumes = 0,
        total_analyses = 0,
        average_ats_score = 0,
        readiness_level = "N/A",
        score_history = [],
        top_missing_skills = []
    } = stats || {};

    const COLORS = ['#d946ef', '#a855f7', '#8b5cf6', '#06b6d4', '#0ea5e9', '#ec4899'];

    return (
        <div className="max-w-7xl mx-auto px-6 py-10 space-y-10 animate-fade-in relative z-10">
            {/* Upper row: Greetings & Call to Action */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-extrabold text-white tracking-tight font-heading">Your Talent Dashboard</h1>
                    <p className="text-slate-400 text-sm mt-1">Review your ATS optimization history and readiness levels.</p>
                </div>
                <button
                    onClick={() => navigate('/analyze')}
                    className="btn-cyber-primary text-white font-semibold px-6 py-3.5 rounded-xl transition-all flex items-center gap-2 group border border-indigo-500/20"
                >
                    <span className="font-heading">Analyze New Resume</span>
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </button>
            </div>

            {/* Empty state check */}
            {total_analyses === 0 ? (
                <Card className="py-16 text-center flex flex-col items-center max-w-2xl mx-auto backdrop-blur-xl bg-slate-950/40 border border-slate-800/40 shadow-2xl">
                    <FileText className="w-16 h-16 text-slate-500 mb-4 animate-bounce" />
                    <h3 className="text-xl font-bold text-slate-200 font-heading">No Resume Analyses Yet</h3>
                    <p className="text-slate-400 text-sm max-w-sm mt-1 mb-6">
                        Upload your PDF/DOCX resume, match it against job descriptions, and see details here.
                    </p>
                    <button
                        onClick={() => navigate('/analyze')}
                        className="btn-cyber-primary text-white font-semibold px-6 py-3 rounded-xl transition-all font-heading border border-indigo-500/20"
                    >
                        Get Started
                    </button>
                </Card>
            ) : (
                <>
                    {/* Stats Metric Cards Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        <Card className="relative overflow-hidden hover:border-indigo-500/30">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Average Score</p>
                                    <h3 className="text-3xl font-black text-white mt-1.5 font-heading">{average_ats_score}%</h3>
                                </div>
                                <div className="p-2.5 bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 rounded-xl">
                                    <Award className="w-5 h-5" />
                                </div>
                            </div>
                            <div className="mt-4 flex items-center gap-1.5 text-xs text-indigo-300 font-medium">
                                <TrendingUp className="w-3.5 h-3.5" />
                                <span>Overall Match Rate</span>
                            </div>
                        </Card>

                        <Card className="hover:border-emerald-500/30">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Resumes Uploaded</p>
                                    <h3 className="text-3xl font-black text-white mt-1.5 font-heading">{total_resumes}</h3>
                                </div>
                                <div className="p-2.5 bg-emerald-550/10 text-emerald-450 border border-emerald-500/20 rounded-xl">
                                    <FileText className="w-5 h-5" />
                                </div>
                            </div>
                            <div className="mt-4 flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                <span>Document profiles active</span>
                            </div>
                        </Card>

                        <Card className="hover:border-cyan-500/30">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Positions Scored</p>
                                    <h3 className="text-3xl font-black text-white mt-1.5 font-heading">{total_analyses}</h3>
                                </div>
                                <div className="p-2.5 bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 rounded-xl">
                                    <Cpu className="w-5 h-5" />
                                </div>
                            </div>
                            <div className="mt-4 flex items-center gap-1.5 text-xs text-cyan-300 font-medium">
                                <Calendar className="w-3.5 h-3.5" />
                                <span>Analyses processed</span>
                            </div>
                        </Card>

                        <Card className="hover:border-fuchsia-500/30">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Interview Readiness</p>
                                    <h3 className="text-3xl font-black text-white mt-1.5 font-heading">{readiness_level}</h3>
                                </div>
                                <div className="p-2.5 bg-fuchsia-500/10 text-fuchsia-300 border border-fuchsia-500/20 rounded-xl">
                                    <CheckCircle2 className="w-5 h-5" />
                                </div>
                            </div>
                            <div className="mt-4 flex items-center gap-1.5 text-xs text-fuchsia-300 font-medium">
                                <span>Based on matching scores</span>
                            </div>
                        </Card>
                    </div>

                    {/* Chart visualizations row */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Area Chart: Score History (2 columns span on lg) */}
                        <Card className="lg:col-span-2 border border-slate-800/40" hover={false}>
                            <h3 className="text-base font-bold text-slate-200 mb-6 font-heading">ATS Score Trend</h3>
                            <div className="h-[280px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={score_history} margin={{ left: -20, right: 10, top: 10, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="scoreColor" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#d946ef" stopOpacity={0.4}/>
                                                <stop offset="95%" stopColor="#d946ef" stopOpacity={0}/>
                                            </linearGradient>
                                        </defs>
                                        <XAxis dataKey="date" stroke="#6b7280" fontSize={11} />
                                        <YAxis domain={[0, 100]} stroke="#6b7280" fontSize={11} />
                                        <Tooltip 
                                            contentStyle={{ backgroundColor: 'rgba(10, 6, 27, 0.95)', borderColor: 'rgba(217, 70, 239, 0.25)', borderRadius: '16px', backdropFilter: 'blur(8px)' }}
                                            labelStyle={{ color: '#c084fc', fontWeight: 'bold' }}
                                            itemStyle={{ color: '#fff' }}
                                            formatter={(value, name, props) => [`${value}%`, `Match Score (${props.payload.job_title})` ]}
                                        />
                                        <Area type="monotone" dataKey="score" stroke="url(#scoreColor)" strokeWidth={3} fillOpacity={1} fill="url(#scoreColor)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </Card>

                        {/* Bar Chart: Missing Skills Frequency */}
                        <Card border={false} className="border border-slate-800/40" hover={false}>
                            <h3 className="text-base font-bold text-slate-200 mb-6 font-heading">Top Missing Skills</h3>
                            {top_missing_skills.length === 0 ? (
                                <div className="h-[280px] flex items-center justify-center text-slate-500 text-xs">
                                    No missing skills logged yet.
                                </div>
                            ) : (
                                <div className="h-[280px] w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={top_missing_skills} layout="vertical" margin={{ left: -10, right: 10, top: 0, bottom: 0 }}>
                                            <XAxis type="number" stroke="#475569" fontSize={10} hide />
                                            <YAxis dataKey="skill" type="category" stroke="#94a3b8" fontSize={11} width={80} axisLine={false} tickLine={false} />
                                            <Tooltip 
                                                contentStyle={{ backgroundColor: 'rgba(10, 6, 27, 0.95)', borderColor: 'rgba(217, 70, 239, 0.25)', borderRadius: '16px', backdropFilter: 'blur(8px)' }}
                                                itemStyle={{ color: '#fff' }}
                                                formatter={(value) => [`${value} times missing`, 'Frequency']}
                                            />
                                            <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={16}>
                                                {top_missing_skills.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            )}
                        </Card>
                    </div>

                    {/* Previous Submissions List */}
                    <Card hover={false} className="border border-slate-800/40">
                        <h3 className="text-base font-bold text-slate-200 mb-6 font-heading">Recent Analysis Reports</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="border-b border-slate-800/60 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                        <th className="pb-4">Target Position</th>
                                        <th className="pb-4">Resume Filename</th>
                                        <th className="pb-4">ATS Match</th>
                                        <th className="pb-4">Date</th>
                                        <th className="pb-4 text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/40 text-sm text-slate-300">
                                    {history.map((item) => (
                                        <tr key={item.id} className="group hover:bg-indigo-500/5 transition-colors">
                                            <td className="py-4 font-semibold text-slate-200">{item.job_title}</td>
                                            <td className="py-4 truncate max-w-[200px]">{item.resume_filename}</td>
                                            <td className="py-4">
                                                <span className={`inline-flex items-center gap-1 font-semibold ${
                                                    item.ats_score >= 80 ? 'text-emerald-400' : item.ats_score >= 65 ? 'text-amber-400' : 'text-red-400'
                                                }`}>
                                                    {item.ats_score}%
                                                </span>
                                            </td>
                                            <td className="py-4 text-slate-450">{item.date}</td>
                                            <td className="py-4 text-right">
                                                <button
                                                    onClick={() => navigate(`/analysis/${item.id}`)}
                                                    className="bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500 hover:text-white border border-indigo-500/20 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shadow-sm"
                                                >
                                                    View Details
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </Card>
                </>
            )}
        </div>
    );
}
