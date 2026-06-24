import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { MessageSquare, Send, Award, Sparkles, BookOpen, AlertCircle, RefreshCw, ChevronRight, HelpCircle, CheckCircle } from 'lucide-react';
import Card from '../components/Card';

export default function Chatbot() {
    const { analysisId } = useParams();
    const navigate = useNavigate();

    const [sessions, setSessions] = useState([]);
    const [history, setHistory] = useState([]);
    const [selectedAnalysis, setSelectedAnalysis] = useState(analysisId || null);
    
    // Chat state
    const [currentSession, setCurrentSession] = useState(null);
    const [messages, setMessages] = useState([]);
    const [totalQuestions, setTotalQuestions] = useState(0);
    const [inputText, setInputText] = useState('');
    const [loadingHistory, setLoadingHistory] = useState(true);
    const [sendingMessage, setSendingMessage] = useState(false);
    const [startingSession, setStartingSession] = useState(false);
    
    const messagesEndRef = useRef(null);

    // Fetch history and sessions list
    useEffect(() => {
        fetchInitialData();
    }, []);

    // Fetch session details if active analysis changes
    useEffect(() => {
        if (selectedAnalysis) {
            startOrResumeSession(selectedAnalysis);
        }
    }, [selectedAnalysis]);

    // Auto scroll chat to bottom
    useEffect(() => {
        scrollToBottom();
    }, [messages, sendingMessage]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const fetchInitialData = async () => {
        try {
            setLoadingHistory(true);
            const [historyRes, sessionsRes] = await Promise.all([
                axios.get('/analysis/history'),
                axios.get('/chat/sessions')
            ]);
            setHistory(historyRes.data);
            setSessions(sessionsRes.data);
        } catch (err) {
            console.error('Error fetching chat dashboard details:', err);
        } finally {
            setLoadingHistory(false);
        }
    };

    const startOrResumeSession = async (analId) => {
        try {
            setStartingSession(true);
            const response = await axios.post('/chat/start', { analysis_id: parseInt(analId) });
            setCurrentSession(response.data.session);
            setMessages(response.data.messages);
            setTotalQuestions(response.data.total_questions);
            
            // Refresh sessions list
            const sessionsRes = await axios.get('/chat/sessions');
            setSessions(sessionsRes.data);
        } catch (err) {
            console.error('Failed to start chat session:', err);
        } finally {
            setStartingSession(false);
        }
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputText.trim() || sendingMessage || !currentSession) return;

        const textToSend = inputText.trim();
        setInputText('');
        setSendingMessage(true);

        // Optimistically add student's message
        const studentMsgOptimistic = {
            id: Date.now(),
            sender: 'student',
            message: textToSend,
            created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, studentMsgOptimistic]);

        try {
            const response = await axios.post('/chat/message', {
                session_id: currentSession.id,
                message: textToSend
            });
            setCurrentSession(response.data.session);
            setMessages(response.data.messages);
        } catch (err) {
            console.error('Failed to send answer to chatbot:', err);
        } finally {
            setSendingMessage(false);
        }
    };

    // Calculate progress stats
    const currentQIndex = currentSession ? currentSession.current_question_index : 0;
    const progressPercent = totalQuestions > 0 ? Math.round((currentQIndex / totalQuestions) * 100) : 0;

    return (
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row gap-6 h-[85vh] animate-fade-in">
            {/* Sidebar: Sessions & Analyzed Resumes List */}
            <div className="w-full md:w-80 shrink-0 flex flex-col gap-5 h-full">
                {/* Session select card */}
                <Card hover={false} className="flex-1 flex flex-col min-h-0 p-5">
                    <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-indigo-400" />
                        <span>Select Practice Target</span>
                    </h3>

                    {loadingHistory ? (
                        <div className="flex-1 flex items-center justify-center">
                            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    ) : history.length === 0 ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-center p-4">
                            <HelpCircle className="w-10 h-10 text-slate-600 mb-2" />
                            <p className="text-xs text-slate-400">Please analyze a resume to begin practicing.</p>
                            <button
                                onClick={() => navigate('/analyze')}
                                className="mt-4 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all"
                            >
                                Analyze Resume
                            </button>
                        </div>
                    ) : (
                        <div className="flex-1 overflow-y-auto space-y-2.5 pr-1.5 custom-scrollbar">
                            {history.map((item) => {
                                const isSelected = parseInt(selectedAnalysis) === item.id;
                                const matchingSession = sessions.find(s => s.analysis_id === item.id);
                                const isCompleted = matchingSession ? matchingSession.is_completed : false;

                                return (
                                    <button
                                        key={item.id}
                                        onClick={() => setSelectedAnalysis(item.id)}
                                        className={`w-full text-left p-3.5 rounded-xl border text-xs transition-all flex flex-col gap-1.5 ${
                                            isSelected
                                                ? 'bg-indigo-600/20 border-indigo-500/40 text-white'
                                                : 'bg-slate-900 border-slate-800 hover:border-slate-700 text-slate-350 hover:text-slate-200'
                                        }`}
                                    >
                                        <div className="flex justify-between items-start w-full">
                                            <span className="font-bold truncate max-w-[170px]">{item.job_title}</span>
                                            {isCompleted ? (
                                                <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-bold shrink-0">Done</span>
                                            ) : matchingSession ? (
                                                <span className="text-[10px] text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 font-bold shrink-0">Active</span>
                                            ) : (
                                                 <span className="text-[10px] text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-850 font-semibold shrink-0">New</span>
                                            )}
                                        </div>
                                        <span className="text-[10px] text-slate-500 truncate w-full">{item.resume_filename}</span>
                                    </button>
                                );
                            })}
                        </div>
                    )}
                </Card>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col h-full">
                {!selectedAnalysis ? (
                    <Card hover={false} className="flex-1 flex flex-col items-center justify-center text-center p-8">
                        <div className="bg-gradient-to-tr from-indigo-600 to-emerald-500 p-4 rounded-2xl text-white shadow-xl shadow-indigo-500/10 mb-4 animate-pulse">
                            <Sparkles className="w-10 h-10" />
                        </div>
                        <h2 className="text-xl font-bold text-slate-200">AI Chat Interview Coach</h2>
                        <p className="text-slate-400 text-sm max-w-sm mt-2 mb-6">
                            Practice interactive mock interviews based on the exact qualifications parsed in your resumes. Choose a practice target on the left to start!
                        </p>
                    </Card>
                ) : startingSession ? (
                    <Card hover={false} className="flex-1 flex items-center justify-center">
                        <div className="flex flex-col items-center gap-4">
                            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                            <p className="text-slate-400 text-sm font-medium">Entering AI interview coaching room...</p>
                        </div>
                    </Card>
                ) : (
                    <div className="flex-1 flex flex-col bg-slate-950/40 border border-slate-800 rounded-3xl overflow-hidden min-h-0 relative">
                        {/* Chat Header */}
                        <div className="bg-slate-900/60 backdrop-blur border-b border-slate-800/80 px-6 py-4 flex flex-col sm:flex-row justify-between sm:items-center gap-4 shrink-0">
                            <div>
                                <h3 className="text-base font-bold text-slate-200">Mock Interview Coach</h3>
                                <p className="text-slate-500 text-xs mt-0.5">Resume-based practice questions</p>
                            </div>
                            
                            {/* Session progress bar */}
                            {totalQuestions > 0 && (
                                <div className="flex items-center gap-3 w-full sm:w-48">
                                    <div className="flex-1 h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-850">
                                        <div 
                                            className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 transition-all duration-300"
                                            style={{ width: `${progressPercent}%` }}
                                        />
                                    </div>
                                    <span className="text-[10px] font-black text-indigo-400 shrink-0">
                                        {currentQIndex} / {totalQuestions} Qs
                                    </span>
                                </div>
                            )}
                        </div>

                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                            {messages.map((msg, index) => {
                                const isInterviewer = msg.sender === 'interviewer';
                                const feedback = msg.feedback;

                                return (
                                    <div key={msg.id || index} className={`flex gap-3 max-w-[85%] ${isInterviewer ? 'mr-auto' : 'ml-auto flex-row-reverse'}`}>
                                        {/* Avatar icon */}
                                        <div className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center text-xs font-black uppercase ${
                                            isInterviewer 
                                                ? 'bg-gradient-to-tr from-indigo-600 to-emerald-500 text-white' 
                                                : 'bg-indigo-600/20 border border-indigo-500/20 text-indigo-400'
                                        }`}>
                                            {isInterviewer ? 'AI' : 'You'}
                                        </div>

                                        <div className="space-y-3">
                                            {/* Chat Bubble bubble */}
                                            <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                                                isInterviewer 
                                                    ? 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none' 
                                                    : 'bg-indigo-600 text-white rounded-tr-none shadow-lg shadow-indigo-600/10'
                                            }`}>
                                                {/* Format message lines nicely */}
                                                {msg.message.split('\n').map((line, idx) => (
                                                    <p key={idx} className={line.trim() === '' ? 'h-3' : 'mb-1.5 last:mb-0'}>
                                                        {line}
                                                    </p>
                                                ))}
                                            </div>

                                            {/* Render evaluation feedback for student answers */}
                                            {feedback && (
                                                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 text-xs text-slate-350 space-y-3 animate-fade-in max-w-lg">
                                                    <div className="flex justify-between items-center border-b border-slate-800/60 pb-2">
                                                        <span className="font-bold text-slate-200 flex items-center gap-1.5">
                                                            <Award className="w-3.5 h-3.5 text-indigo-400" />
                                                            <span>Coach Review</span>
                                                        </span>
                                                        <span className={`font-black uppercase tracking-wider px-2 py-0.5 rounded text-[10px] border ${
                                                            feedback.rating === 'Excellent' 
                                                                ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                                                                : feedback.rating === 'Good'
                                                                ? 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20'
                                                                : feedback.rating === 'Satisfactory'
                                                                ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
                                                                : 'text-red-400 bg-red-500/10 border-red-500/20'
                                                        }`}>
                                                            {feedback.rating}
                                                        </span>
                                                    </div>

                                                    {feedback.matched_keywords && feedback.matched_keywords.length > 0 && (
                                                        <div className="space-y-1">
                                                            <span className="font-bold text-slate-400">Strengths Mentioned:</span>
                                                            <div className="flex flex-wrap gap-1 mt-1">
                                                                {feedback.matched_keywords.map((kw, kIdx) => (
                                                                    <span key={kIdx} className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-semibold">
                                                                        {kw}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {feedback.missing_keywords && feedback.missing_keywords.length > 0 && (
                                                        <div className="space-y-1">
                                                            <span className="font-bold text-slate-400">Consider Mentioning:</span>
                                                            <div className="flex flex-wrap gap-1 mt-1">
                                                                {feedback.missing_keywords.map((kw, kIdx) => (
                                                                    <span key={kIdx} className="bg-slate-950 text-slate-500 px-2 py-0.5 rounded text-[10px] font-semibold border border-slate-850">
                                                                        {kw}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    <div className="text-slate-400 border-t border-slate-800/40 pt-2 flex items-start gap-1.5 leading-relaxed">
                                                        <BookOpen className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                                                        <p>{feedback.tip}</p>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}

                            {/* Typing indicator bubble */}
                            {sendingMessage && (
                                <div className="flex gap-3 max-w-[80%] mr-auto">
                                    <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-emerald-500 text-white shrink-0 flex items-center justify-center text-xs font-black uppercase">
                                        AI
                                    </div>
                                    <div className="bg-slate-900 border border-slate-800 text-slate-400 p-4 rounded-2xl rounded-tl-none flex items-center gap-1.5">
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            )}

                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Form at bottom */}
                        <div className="bg-slate-900/60 border-t border-slate-800/80 px-6 py-4 shrink-0">
                            {currentSession?.is_completed ? (
                                <div className="flex items-center justify-center gap-4 py-1 text-slate-350 text-xs">
                                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                                    <span>This mock interview has completed successfully. Choose another target on the left to start again.</span>
                                </div>
                            ) : (
                                <form onSubmit={handleSendMessage} className="flex gap-3">
                                    <input
                                        type="text"
                                        value={inputText}
                                        onChange={(e) => setInputText(e.target.value)}
                                        placeholder="Type your detailed response here..."
                                        disabled={sendingMessage || !currentSession}
                                        className="flex-1 bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl px-4 py-3 text-slate-200 placeholder-slate-650 outline-none text-sm transition-all"
                                        required
                                    />
                                    <button
                                        type="submit"
                                        disabled={sendingMessage || !inputText.trim() || !currentSession}
                                        className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/40 text-white px-5 py-3 rounded-xl transition-all flex items-center justify-center shrink-0"
                                    >
                                        <Send className="w-4 h-4" />
                                    </button>
                                </form>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
