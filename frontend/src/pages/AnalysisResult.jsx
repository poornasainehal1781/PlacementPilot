import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
    Download, ArrowLeft, CheckCircle, XCircle, AlertTriangle, 
    FileText, Award, Layers, Sparkles, User, Mail, Phone, BookOpen, Briefcase
} from 'lucide-react';
import Card from '../components/Card';

export default function AnalysisResult() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [downloading, setDownloading] = useState(false);
    const [activeTab, setActiveTab] = useState('summary');

    useEffect(() => {
        fetchResult();
    }, [id]);

    const fetchResult = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`/analysis/${id}`);
            setData(response.data);
        } catch (err) {
            console.error('Error fetching analysis details:', err);
            setError('Failed to fetch analysis details.');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPDF = async () => {
        try {
            setDownloading(true);
            const response = await axios.get(`/analysis/${id}/report`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `ATS_Report_${data.job_description.title.replace(/\s+/g, '_')}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Error downloading PDF:', err);
        } finally {
            setDownloading(false);
        }
    };

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-12 flex items-center justify-center min-h-[60vh]">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-slate-400 font-medium">Loading match metrics...</p>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-12">
                <Card className="border-red-500/20 bg-red-500/5 p-8 flex flex-col items-center text-center">
                    <XCircle className="w-12 h-12 text-red-400 mb-3" />
                    <h3 className="text-xl font-bold text-slate-200">Analysis Not Found</h3>
                    <p className="text-slate-400 text-sm mt-1 mb-6">
                        We could not retrieve the details of this resume analysis.
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

    const { analysis, job_description, resume, questions } = data;
    const recs = analysis.recommendations || {};
    const missingSkills = analysis.missing_skills || [];
    const resumeSkills = resume.skills || [];
    const matchedSkills = job_description.skills_required?.filter(s => !missingSkills.includes(s)) || [];

    // Score Color calculations
    const score = analysis.ats_score;
    const scoreColorClass = score >= 80 ? 'text-emerald-400' : score >= 60 ? 'text-amber-400' : 'text-red-400';
    const scoreStrokeClass = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444';

    return (
        <div className="max-w-7xl mx-auto px-6 py-10 space-y-8 animate-fade-in">
            {/* Header row */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800/60 pb-6">
                <div>
                    <button
                        onClick={() => navigate('/')}
                        className="flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors mb-3"
                    >
                        <ArrowLeft className="w-3.5 h-3.5" />
                        <span>Back to Dashboard</span>
                    </button>
                    <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                        Match Audit: {job_description.title}
                    </h1>
                    <p className="text-slate-400 text-xs md:text-sm mt-1">
                        Resume profile evaluated: <span className="text-slate-200">{resume.filename}</span>
                    </p>
                </div>
                
                <div className="flex gap-3">
                    <button
                        onClick={handleDownloadPDF}
                        disabled={downloading}
                        className="bg-slate-900 border border-slate-850 hover:bg-slate-850 text-slate-200 hover:text-white px-5 py-3 rounded-xl text-sm font-semibold transition-all flex items-center gap-2"
                    >
                        <Download className="w-4 h-4" />
                        <span>{downloading ? 'Downloading...' : 'PDF Report'}</span>
                    </button>

                    <button
                        onClick={() => navigate(`/analysis/${analysis.id}/prep`)}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-3 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 shadow-lg shadow-indigo-600/10"
                    >
                        <Sparkles className="w-4 h-4" />
                        <span>Start Prep ({questions.length})</span>
                    </button>
                </div>
            </div>
            {/* Tab Navigation */}
            <div className="flex flex-wrap border-b border-slate-800/80 gap-6 mt-2">
                <button 
                    onClick={() => setActiveTab('summary')}
                    className={`pb-4 text-xs font-bold uppercase tracking-wider transition-all relative outline-none ${
                        activeTab === 'summary' ? 'text-white font-extrabold' : 'text-slate-500 hover:text-slate-300'
                    }`}
                >
                    Summary Dashboard
                    {activeTab === 'summary' && (
                        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-indigo-500"></div>
                    )}
                </button>
                <button 
                    onClick={() => setActiveTab('resume_summary')}
                    className={`pb-4 text-xs font-bold uppercase tracking-wider transition-all relative outline-none ${
                        activeTab === 'resume_summary' ? 'text-white font-extrabold' : 'text-slate-500 hover:text-slate-300'
                    }`}
                >
                    Resume Summary Profile
                    {activeTab === 'resume_summary' && (
                        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-indigo-500"></div>
                    )}
                </button>
                <button 
                    onClick={() => setActiveTab('improvements')}
                    className={`pb-4 text-xs font-bold uppercase tracking-wider transition-all relative outline-none ${
                        activeTab === 'improvements' ? 'text-white font-extrabold' : 'text-slate-500 hover:text-slate-300'
                    }`}
                >
                    Actionable Improvements ({recs.actionable_improvements?.length || 0})
                    {activeTab === 'improvements' && (
                        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-indigo-500"></div>
                    )}
                </button>
                <button 
                    onClick={() => setActiveTab('keywords')}
                    className={`pb-4 text-xs font-bold uppercase tracking-wider transition-all relative outline-none ${
                        activeTab === 'keywords' ? 'text-white font-extrabold' : 'text-slate-500 hover:text-slate-300'
                    }`}
                >
                    Keywords & Skills Mapping
                    {activeTab === 'keywords' && (
                        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-indigo-500"></div>
                    )}
                </button>
                <button 
                    onClick={() => setActiveTab('parsed')}
                    className={`pb-4 text-xs font-bold uppercase tracking-wider transition-all relative outline-none ${
                        activeTab === 'parsed' ? 'text-white font-extrabold' : 'text-slate-500 hover:text-slate-300'
                    }`}
                >
                    Parsed Resume Sections
                    {activeTab === 'parsed' && (
                        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-indigo-500"></div>
                    )}
                </button>
            </div>

            {/* Tab: Summary Dashboard */}
            {activeTab === 'summary' && (
                <div className="space-y-8 animate-fade-in">
                    {score < 80 && (
                        <Card hover={false} className={`border-l-4 p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 animate-fade-in ${
                            score < 60 
                                ? 'border-red-500 bg-red-500/5' 
                                : 'border-amber-500 bg-amber-500/5'
                        }`}>
                            <div className="flex items-start gap-4">
                                <div className={`p-2 rounded-xl shrink-0 mt-0.5 ${
                                    score < 60 ? 'bg-red-500/10 text-red-400' : 'bg-amber-500/10 text-amber-400'
                                }`}>
                                    <AlertTriangle className="w-5 h-5" />
                                </div>
                                <div>
                                    <h4 className="text-sm font-bold text-white flex items-center gap-2">
                                        <span>{score < 60 ? 'Critical Match Warning' : 'Match Rate Improvement Recommended'}</span>
                                        <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-md ${
                                            score < 60 ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                        }`}>
                                            Low ATS Score ({score}%)
                                        </span>
                                    </h4>
                                    <p className="text-xs text-slate-400 mt-2 leading-relaxed max-w-2xl">
                                        Your resume has low contextual alignment with the requirements of this role. 
                                        We strongly recommend <strong className="text-slate-200">modifying and changing your resume</strong> to incorporate the missing skills and improvements suggested below so that you can achieve a good ATS score.
                                    </p>
                                </div>
                            </div>
                            <div className="flex flex-col sm:flex-row md:flex-col gap-2.5 w-full md:w-auto shrink-0">
                                <button
                                    onClick={() => setActiveTab('improvements')}
                                    className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all border text-center ${
                                        score < 60
                                            ? 'bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white border-red-500/20'
                                            : 'bg-amber-500/10 text-amber-400 hover:bg-amber-500 hover:text-white border-amber-500/20'
                                    }`}
                                >
                                    View Actionable Improvements
                                </button>
                                <button
                                    onClick={() => navigate('/analyze')}
                                    className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl text-xs font-bold transition-all text-center shadow-lg shadow-indigo-600/10"
                                >
                                    Upload Revised Resume
                                </button>
                            </div>
                        </Card>
                    )}

                    {/* Score & Profile Summary Panels */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Radial Gauge Card */}
                        <Card hover={false} className="flex flex-col items-center justify-center py-8">
                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-6">Overall ATS Score</p>
                            <div className="relative w-36 h-36 flex items-center justify-center">
                                <svg className="w-full h-full transform -rotate-90">
                                    <circle
                                        cx="72"
                                        cy="72"
                                        r="64"
                                        className="stroke-slate-800"
                                        strokeWidth="8"
                                        fill="transparent"
                                    />
                                    <circle
                                        cx="72"
                                        cy="72"
                                        r="64"
                                        stroke={scoreStrokeClass}
                                        strokeWidth="8"
                                        fill="transparent"
                                        strokeDasharray={2 * Math.PI * 64}
                                        strokeDashoffset={2 * Math.PI * 64 * (1 - score / 100)}
                                        strokeLinecap="round"
                                        className="transition-all duration-1000 ease-out"
                                    />
                                </svg>
                                <div className="absolute flex flex-col items-center justify-center">
                                    <span className={`text-3xl font-black ${scoreColorClass}`}>{score}%</span>
                                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider mt-0.5">Rating</span>
                                </div>
                            </div>
                        </Card>

                        {/* Similarity metrics Card */}
                        <Card hover={false} className="flex flex-col justify-between py-8">
                            <div>
                                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Semantic Context Match</p>
                                <div className="flex items-baseline gap-2">
                                    <h3 className="text-4xl font-extrabold text-white">{analysis.similarity_score}%</h3>
                                    <span className="text-xs text-indigo-400 font-semibold bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">TF-IDF Index</span>
                                </div>
                                <p className="text-xs text-slate-400 leading-relaxed mt-4">
                                    Calculated using cosine similarity comparison. This scores the contextual alignment of your experience vocabulary against the role requirements.
                                </p>
                            </div>
                            <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-4 border-t border-slate-800/80 pt-4">
                                <Layers className="w-3.5 h-3.5 text-indigo-400" />
                                <span>High Keyword density is crucial</span>
                            </div>
                        </Card>

                        {/* Profile contact Details Card */}
                        <Card hover={false} className="py-8 space-y-4">
                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Parsed Contact Details</p>
                            
                            <div className="space-y-3.5 text-sm">
                                <div className="flex items-center gap-3 text-slate-300">
                                    <div className="p-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-400">
                                        <User className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-500 font-medium">Full Name</p>
                                        <p className="font-semibold text-slate-200 leading-tight">
                                            {resume.name || resume.filename?.replace(/^user_\d+_/, '').split('.')[0] || 'Parsed Candidate'}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 text-slate-300">
                                    <div className="p-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-400">
                                        <Mail className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-500 font-medium">Email Address</p>
                                        <p className="font-semibold text-slate-200 leading-tight">
                                            {resume.email || 'No email detected'}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 text-slate-300">
                                    <div className="p-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-400">
                                        <Phone className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-500 font-medium">Phone Number</p>
                                        <p className="font-semibold text-slate-200 leading-tight">
                                            {resume.phone || 'No phone number detected'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </div>

                    {/* Recommendations Panels */}
                    <Card hover={false} className="p-6 space-y-6">
                        <div className="flex items-start gap-3">
                            <div className="p-2.5 bg-indigo-600/20 text-indigo-400 border border-indigo-500/20 rounded-xl mt-0.5">
                                <Award className="w-5 h-5" />
                            </div>
                            <div>
                                <h3 className="text-base font-bold text-slate-200">Overall Match Evaluation</h3>
                                <p className="text-sm text-slate-400 leading-relaxed mt-1">
                                    {recs.general_feedback}
                                </p>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            {/* Tab: Actionable Improvements */}
            {activeTab === 'improvements' && (
                <div className="space-y-6 animate-fade-in">
                    {recs.formatting_suggestions?.length > 0 && (
                        <Card hover={false} className="p-6 space-y-4">
                            <h4 className="text-sm font-bold text-slate-300 flex items-center gap-1.5 border-b border-slate-850 pb-3">
                                <AlertTriangle className="w-4 h-4 text-amber-400" />
                                <span>Structural & Content Recommendations</span>
                            </h4>
                            <ul className="grid grid-cols-1 md:grid-cols-2 gap-3.5 pl-2">
                                {recs.formatting_suggestions.map((sug, index) => (
                                    <li key={index} className="text-xs text-slate-400 flex items-start gap-2 bg-slate-950 border border-slate-850 p-3 rounded-xl">
                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                                        <span>{sug}</span>
                                    </li>
                                ))}
                            </ul>
                        </Card>
                    )}

                    {recs.actionable_improvements?.length > 0 && (
                        <Card hover={false} className="p-6 space-y-4 border-indigo-500/10 bg-slate-900/20">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-indigo-600/25 text-indigo-400 border border-indigo-500/20 rounded-xl">
                                    <Sparkles className="w-5 h-5 animate-pulse" />
                                </div>
                                <div>
                                    <h3 className="text-base font-extrabold text-slate-200">Actionable Resume Improvements</h3>
                                    <p className="text-xs text-slate-400 mt-0.5">Step-by-step modifications to align your resume with the job requirements</p>
                                </div>
                            </div>
                            
                            <div className="overflow-x-auto mt-4 border border-slate-800 rounded-xl bg-slate-950/40">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-300 text-[11px] font-bold uppercase tracking-wider">
                                            <th className="py-3 px-4 w-[20%]">Section / Location</th>
                                            <th className="py-3 px-4 w-[25%]">What to Change</th>
                                            <th className="py-3 px-4">Action Strategy (How-To)</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-850/60 text-xs text-slate-300">
                                        {recs.actionable_improvements.map((imp, idx) => (
                                            <tr key={idx} className="hover:bg-slate-900/30 transition-colors">
                                                <td className="py-3.5 px-4 font-semibold text-indigo-400">
                                                    <span className="inline-block bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider">
                                                        {imp.where}
                                                    </span>
                                                </td>
                                                <td className="py-3.5 px-4 font-medium text-slate-200">
                                                    {imp.what}
                                                </td>
                                                <td className="py-3.5 px-4 text-slate-400 leading-relaxed">
                                                    {imp.how}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>
                    )}
                </div>
            )}

            {/* Tab: Keywords & Skills */}
            {activeTab === 'keywords' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in">
                    {/* Matched Skills */}
                    <Card hover={false} className="border-emerald-500/10 bg-slate-900/40">
                        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                            <CheckCircle className="w-4.5 h-4.5 text-emerald-400" />
                            <span>Matched Keywords ({matchedSkills.length})</span>
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {matchedSkills.length === 0 ? (
                                <span className="text-xs text-slate-500 italic">No matching keywords detected. Check your spelling or vocabulary.</span>
                            ) : (
                                matchedSkills.map((skill, index) => (
                                    <span 
                                        key={index}
                                        className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-xl"
                                    >
                                        {skill}
                                    </span>
                                ))
                            )}
                        </div>
                    </Card>

                    {/* Missing Skills */}
                    <Card hover={false} className="border-red-500/10 bg-slate-900/40">
                        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                            <AlertTriangle className="w-4.5 h-4.5 text-amber-500" />
                            <span>Missing Role Keywords ({missingSkills.length})</span>
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {missingSkills.length === 0 ? (
                                <span className="text-xs text-emerald-400 font-semibold">Perfect keyword alignment! No key skills missing.</span>
                            ) : (
                                missingSkills.map((skill, index) => (
                                    <span 
                                        key={index}
                                        className="text-xs font-semibold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-xl"
                                    >
                                        {skill}
                                    </span>
                                ))
                            )}
                        </div>
                    </Card>
                </div>
            )}

            {/* Tab: Resume Summary Profile */}
            {activeTab === 'resume_summary' && (
                <div className="space-y-6 animate-fade-in">
                    {/* Key Skills identified */}
                    <Card hover={false} className="border-indigo-500/10 bg-slate-900/40">
                        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                            <Layers className="w-4.5 h-4.5 text-indigo-400" />
                            <span>Extracted Core Skills Profile</span>
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {recs.resume_summary?.key_skills && recs.resume_summary.key_skills.length > 0 ? (
                                recs.resume_summary.key_skills.map((skill, index) => (
                                    <span 
                                        key={index}
                                        className="text-xs font-semibold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-3 py-1.5 rounded-xl"
                                    >
                                        {skill}
                                    </span>
                                ))
                            ) : (
                                <span className="text-xs text-slate-500 italic">No explicit technical skills parsed or mapped in the summary.</span>
                            )}
                        </div>
                    </Card>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Projects Portfolio */}
                        <Card hover={false} className="border-indigo-500/10 bg-slate-900/40">
                            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                                <Sparkles className="w-4.5 h-4.5 text-indigo-400" />
                                <span>Project Portfolio & Tech Stack</span>
                            </h3>
                            <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                                {recs.resume_summary?.projects && recs.resume_summary.projects.length > 0 ? (
                                    recs.resume_summary.projects.map((proj, idx) => (
                                        <div key={idx} className="bg-slate-950/60 border border-slate-850 p-4 rounded-xl space-y-2.5">
                                            <h4 className="text-xs font-black text-white uppercase tracking-wider">{proj.title}</h4>
                                            {proj.technologies && proj.technologies.length > 0 && (
                                                <div className="flex flex-wrap gap-1.5">
                                                    {proj.technologies.map((tech, tIdx) => (
                                                        <span key={tIdx} className="text-[10px] font-bold text-slate-350 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                                                            {tech}
                                                        </span>
                                                    ))}
                                                </div>
                                            )}
                                            {proj.description && (
                                                <p className="text-[11px] text-slate-400 leading-relaxed mt-1">{proj.description}</p>
                                            )}
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-xs text-slate-500 italic">No structured project records resolved.</p>
                                )}
                            </div>
                        </Card>

                        {/* Experience Highlights */}
                        <Card hover={false} className="border-indigo-500/10 bg-slate-900/40">
                            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                                <Briefcase className="w-4.5 h-4.5 text-indigo-400" />
                                <span>Internship & Experience Highlights</span>
                            </h3>
                            <div className="space-y-3.5 max-h-[400px] overflow-y-auto pr-2">
                                {recs.resume_summary?.internship_highlights && recs.resume_summary.internship_highlights.length > 0 ? (
                                    recs.resume_summary.internship_highlights.map((highlight, idx) => (
                                        <div key={idx} className="text-xs text-slate-350 bg-slate-950/60 border border-slate-850 p-3.5 rounded-xl leading-relaxed flex items-start gap-2.5">
                                            <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                                            <span>{highlight}</span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-xs text-slate-500 italic">No structured work or experience highlights detected.</p>
                                )}
                            </div>
                        </Card>
                    </div>

                    {/* Claims Cards */}
                    <Card hover={false} className="border-indigo-500/10 bg-slate-900/40">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
                            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                                <FileText className="w-4.5 h-4.5 text-indigo-400" />
                                <span>Resume Claims & Ownership Triggers</span>
                            </h3>
                            <span className="text-[10px] font-black uppercase text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-md">
                                Critical Interview Targets
                            </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed mb-4">
                            The system detected the following high-value action statements and implementation claims on your resume. 
                            Our mock interviewer has prepared deep verification questions to test your real ownership and technical depth on these items:
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {recs.resume_summary?.strong_claims && recs.resume_summary.strong_claims.length > 0 ? (
                                recs.resume_summary.strong_claims.map((claim, idx) => (
                                    <div key={idx} className="bg-slate-950/60 border border-l-2 border-l-indigo-500 border-slate-850 p-3.5 rounded-r-xl text-xs text-slate-300 leading-relaxed">
                                        {claim}
                                    </div>
                                ))
                            ) : (
                                <p className="text-xs text-slate-500 italic col-span-2">No strong action verb claims parsed.</p>
                            )}
                        </div>
                    </Card>
                </div>
            )}

            {/* Tab: Parsed Sections */}
            {activeTab === 'parsed' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in">
                    <Card hover={false}>
                        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                            <Briefcase className="w-4.5 h-4.5 text-indigo-400" />
                            <span>Parsed Work History</span>
                        </h3>
                        <div className="space-y-3.5 max-h-[400px] overflow-y-auto pr-2">
                            {resume.experience && resume.experience.length > 0 ? (
                                resume.experience.map((exp, idx) => (
                                    <div key={idx} className="text-xs text-slate-400 bg-slate-950/60 border border-slate-850 p-3 rounded-xl leading-relaxed">
                                        {exp}
                                    </div>
                                ))
                            ) : (
                                <p className="text-xs text-slate-500 italic">No structured work experience parsed.</p>
                            )}
                        </div>
                    </Card>

                    <Card hover={false}>
                        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                            <BookOpen className="w-4.5 h-4.5 text-indigo-400" />
                            <span>Parsed Education History</span>
                        </h3>
                        <div className="space-y-3.5 max-h-[400px] overflow-y-auto pr-2">
                            {resume.education && resume.education.length > 0 ? (
                                resume.education.map((edu, idx) => (
                                    <div key={idx} className="text-xs text-slate-400 bg-slate-950/60 border border-slate-850 p-3 rounded-xl leading-relaxed">
                                        {edu}
                                    </div>
                                ))
                            ) : (
                                <p className="text-xs text-slate-500 italic">No structured education parsed.</p>
                            )}
                        </div>
                    </Card>
                </div>
            )}
        </div>
    );
}
