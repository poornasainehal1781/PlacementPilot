import React, { useState, useRef } from 'react';
import { Upload, File, AlertCircle, CheckCircle } from 'lucide-react';

export default function FileUpload({ onFileSelect, file, error, setError }) {
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const validateAndSelect = (selectedFile) => {
        setError(null);
        if (!selectedFile) return;

        const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
        if (fileExtension !== 'pdf' && fileExtension !== 'docx') {
            setError("Invalid file type. Only PDF and DOCX documents are supported.");
            return;
        }

        const fileSizeMB = selectedFile.size / (1024 * 1024);
        if (fileSizeMB > 16) {
            setError("File size exceeds 16MB limit.");
            return;
        }

        onFileSelect(selectedFile);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndSelect(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            validateAndSelect(e.target.files[0]);
        }
    };

    const onButtonClick = () => {
        fileInputRef.current.click();
    };

    return (
        <div className="w-full">
            <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".pdf,.docx"
                onChange={handleChange}
            />

            <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={onButtonClick}
                className={`w-full py-8 px-6 border-2 border-dashed rounded-2xl cursor-pointer flex flex-col items-center justify-center transition-all duration-300 ${
                    dragActive
                        ? 'border-indigo-500 bg-indigo-500/10 shadow-lg shadow-indigo-500/5 animate-pulse-ring'
                        : file
                        ? 'border-emerald-500 bg-emerald-500/5 shadow-lg shadow-emerald-500/5'
                        : 'border-slate-800/80 bg-slate-950/40 hover:border-indigo-500/30 hover:bg-slate-950/60'
                }`}
            >
                {file ? (
                    <div className="flex flex-col items-center text-center">
                        <div className="w-14 h-14 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-2xl flex items-center justify-center mb-4">
                            <File className="w-6 h-6 animate-pulse" />
                        </div>
                        <h4 className="text-sm font-semibold text-slate-200 mb-1 max-w-[250px] truncate font-heading">
                            {file.name}
                        </h4>
                        <p className="text-xs text-slate-400 mb-3">
                            {(file.size / 1024).toFixed(1)} KB
                        </p>
                        <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                            <CheckCircle className="w-3.5 h-3.5" />
                            Ready to Analyze
                        </span>
                    </div>
                ) : (
                    <div className="flex flex-col items-center text-center group">
                        <div className="w-14 h-14 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-2xl flex items-center justify-center mb-4 transition-all duration-300 group-hover:scale-105 group-hover:border-indigo-500/40">
                            <Upload className="w-6 h-6" />
                        </div>
                        <h4 className="text-sm font-semibold text-slate-200 mb-1 font-heading">
                            Drag & drop your resume file
                        </h4>
                        <p className="text-xs text-slate-400 mb-4">
                            Supports PDF and DOCX formats (Max 16MB)
                        </p>
                        <button
                            type="button"
                            className="bg-indigo-500 hover:bg-indigo-600 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-md shadow-indigo-500/20 cursor-pointer border border-indigo-500/30"
                        >
                            Browse Files
                        </button>
                    </div>
                )}
            </div>

            {error && (
                <div className="mt-3 flex items-center gap-2 bg-red-500/10 border border-red-500/20 text-red-400 p-3.5 rounded-xl text-xs">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
}
