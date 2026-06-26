import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Sparkles, Terminal, FileText, PenTool, CheckCircle, BrainCircuit } from 'lucide-react';
import Card from '../components/Card';
import FileUpload from '../components/FileUpload';

export default function UploadAnalyze() {
    const navigate = useNavigate();
    const [file, setFile] = useState(null);
    const [uploadError, setUploadError] = useState(null);
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    
    // UI Loading steps
    const [loading, setLoading] = useState(false);
    const [loadingStep, setLoadingStep] = useState(0);

    const steps = [
        "Uploading and parsing resume PDF/DOCX format...",
        "Identifying core skill sets and candidate profile...",
        "Scoring document layout, contact details, and structure...",
        "Running TF-IDF match with job description vocabulary...",
        "Generating customized interview questions and reports..."
    ];

    useEffect(() => {
        let interval;
        if (loading) {
            interval = setInterval(() => {
                setLoadingStep((prev) => {
                    if (prev < steps.length - 1) {
                        return prev + 1;
                    }
                    return prev;
                });
            }, 1800);
        } else {
            setLoadingStep(0);
        }
        return () => clearInterval(interval);
    }, [loading]);

    const handleAnalyze = async (e) => {
        e.preventDefault();
        setUploadError(null);

        if (!file) {
            setUploadError("Please upload a resume file first.");
            return;
        }

        if (!jobTitle.trim() || !jobDescription.trim()) {
            setUploadError("Please enter both the Job Title and Job Description.");
            return;
        }

        try {
            setLoading(true);
            
            // 1. Upload Resume
            const formData = new FormData();
            formData.append('file', file);
            const uploadRes = await axios.post('/resumes/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const resumeId = uploadRes.data.resume.id;

            // 2. Run analysis
            const analyzeRes = await axios.post('/analysis/analyze', {
                resume_id: resumeId,
                job_title: jobTitle,
                job_description: jobDescription
            });

            const analysisId = analyzeRes.data.analysis.id;
            
            // Allow a small delay for smooth transition
            setTimeout(() => {
                setLoading(false);
                navigate(`/analysis/${analysisId}`);
            }, 1000);

        } catch (err) {
            console.error('Error analyzing resume:', err);
            setUploadError(err.response?.data?.error || "Failed to analyze resume. Please try again.");
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="max-w-4xl mx-auto px-6 py-20 flex flex-col items-center justify-center min-h-[70vh] relative z-10 animate-fade-in">
                <div className="w-24 h-24 relative mb-8 flex items-center justify-center">
                    <div className="absolute inset-0 border-4 border-indigo-500/10 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-t-indigo-500 rounded-full animate-spin"></div>
                    <BrainCircuit className="w-8 h-8 text-indigo-400 animate-pulse" />
                </div>
                
                <h3 className="text-xl font-bold text-slate-200 mb-2 font-heading">Analyzing Optimization Score</h3>
                <p className="text-sm text-indigo-300 font-semibold bg-indigo-550/10 px-4 py-1.5 rounded-full border border-indigo-500/20 mb-8 animate-pulse">
                    Step {loadingStep + 1} of {steps.length}
                </p>
                
                <div className="w-full max-w-md bg-slate-950/40 border border-slate-800/40 p-6 rounded-2xl backdrop-blur-xl">
                    <div className="space-y-4">
                        {steps.map((step, idx) => (
                            <div key={idx} className={`flex items-center gap-3 transition-opacity duration-300 ${
                                idx < loadingStep ? 'text-emerald-400 opacity-100' :
                                idx === loadingStep ? 'text-indigo-400 opacity-100' :
                                'text-slate-650 opacity-50'
                            }`}>
                                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                                    idx < loadingStep ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                                    idx === loadingStep ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse-ring' :
                                    'bg-slate-950 text-slate-600 border border-slate-800'
                                }`}>
                                    {idx < loadingStep ? "✓" : idx + 1}
                                </div>
                                <span className="text-xs font-medium">{step}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-6 py-10 space-y-8 relative z-10">
            <div>
                <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-2 font-heading">
                    <Sparkles className="w-7 h-7 text-indigo-450 animate-pulse" />
                    <span>AI Resume Matcher</span>
                </h1>
                <p className="text-slate-400 text-sm mt-1">
                    Upload your resume and the target job description to audit your ATS performance.
                </p>
            </div>

            <form onSubmit={handleAnalyze} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Side: File Upload */}
                <div className="space-y-6">
                    <h3 className="text-base font-bold text-slate-200 flex items-center gap-2 font-heading">
                        <FileText className="w-4 h-4 text-slate-400" />
                        <span>Step 1: Upload Resume</span>
                    </h3>
                    <Card hover={false} className="p-8 backdrop-blur-xl bg-slate-950/40 border border-slate-800/40 shadow-2xl">
                        <FileUpload 
                            onFileSelect={setFile} 
                            file={file} 
                            error={uploadError && !jobTitle ? uploadError : null} 
                            setError={setUploadError} 
                        />
                    </Card>
                </div>

                {/* Right Side: Job Description Details */}
                <div className="space-y-6">
                    <h3 className="text-base font-bold text-slate-200 flex items-center gap-2 font-heading">
                        <PenTool className="w-4 h-4 text-slate-400" />
                        <span>Step 2: Enter Job Description</span>
                    </h3>
                    <Card hover={false} className="p-8 space-y-5 backdrop-blur-xl bg-slate-950/40 border border-slate-800/40 shadow-2xl">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Target Job Title
                            </label>
                            <input
                                type="text"
                                value={jobTitle}
                                onChange={(e) => setJobTitle(e.target.value)}
                                placeholder="e.g. Full-Stack Software Engineer"
                                className="w-full bg-slate-950/80 border border-slate-800/80 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3 px-4 text-slate-200 placeholder-slate-600 outline-none transition-all duration-300 text-sm"
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Paste Job Description
                            </label>
                            <textarea
                                value={jobDescription}
                                onChange={(e) => setJobDescription(e.target.value)}
                                placeholder="Paste the complete job description text including qualifications, responsibilities, and skill requirements..."
                                rows={8}
                                className="w-full bg-slate-950/80 border border-slate-800/80 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-3 px-4 text-slate-200 placeholder-slate-600 outline-none transition-all duration-300 text-sm resize-none"
                                required
                            />
                        </div>

                        {uploadError && jobTitle && (
                            <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 p-3.5 rounded-xl">
                                {uploadError}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="w-full btn-cyber-primary text-white font-semibold py-3.5 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 group cursor-pointer border border-indigo-500/25"
                        >
                            <Terminal className="w-4 h-4" />
                            <span>Analyze Match & Prepare</span>
                        </button>
                    </Card>
                </div>
            </form>
        </div>
    );
}
