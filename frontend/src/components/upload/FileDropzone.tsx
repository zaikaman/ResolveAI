/**
 * FileDropzone component - react-dropzone wrapper for document upload
 * Design aligned with landing page styling
 */

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '../common/Button';
import { cn } from '../../utils/cn';

interface FileDropzoneProps {
    onFileSelect: (file: File) => void;
    isUploading?: boolean;
    uploadProgress?: number;
    acceptedTypes?: string[];
    maxSize?: number; // in bytes
    className?: string;
}

const DEFAULT_ACCEPTED_TYPES = ['image/png', 'image/jpeg', 'image/webp'];
const DEFAULT_MAX_SIZE = 10 * 1024 * 1024; // 10MB

export function FileDropzone({
    onFileSelect,
    isUploading = false,
    uploadProgress = 0,
    acceptedTypes = DEFAULT_ACCEPTED_TYPES,
    maxSize = DEFAULT_MAX_SIZE,
    className,
}: FileDropzoneProps) {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [error, setError] = useState<string | null>(null);

    const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
        setError(null);

        if (rejectedFiles.length > 0) {
            const rejection = rejectedFiles[0];
            if (rejection.errors[0]?.code === 'file-too-large') {
                setError(`File too large. Maximum size is ${maxSize / 1024 / 1024}MB`);
            } else if (rejection.errors[0]?.code === 'file-invalid-type') {
                setError('Invalid file type. Please upload PNG, JPEG, or WebP images.');
            } else {
                setError('File not accepted. Please try again.');
            }
            return;
        }

        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            setSelectedFile(file);
            onFileSelect(file);
        }
    }, [onFileSelect, maxSize]);

    const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
        onDrop,
        accept: acceptedTypes.reduce((acc: Record<string, string[]>, type) => {
            acc[type] = [];
            return acc;
        }, {}),
        maxSize,
        multiple: false,
        disabled: isUploading,
    });

    const removeFile = () => {
        setSelectedFile(null);
        setError(null);
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className={cn("space-y-4", className)}>
            {/* Dropzone */}
            <div
                {...getRootProps()}
                className={cn(
                    "relative border-2 border-dashed rounded-xl p-8 transition-all cursor-pointer",
                    isDragActive && !isDragReject && "border-main bg-main3",
                    isDragReject && "border-red-400 bg-red-50",
                    !isDragActive && !isDragReject && "border-slate-200 hover:border-main hover:bg-main3/50",
                    isUploading && "opacity-50 cursor-not-allowed",
                    error && "border-red-300 bg-red-50"
                )}
            >
                <input {...getInputProps()} />

                <div className="flex flex-col items-center text-center">
                    <div className={cn(
                        "p-4 rounded-full mb-4",
                        isDragActive ? "bg-main2" : "bg-slate-100"
                    )}>
                        <Upload className={cn(
                            "h-8 w-8",
                            isDragActive ? "text-main" : "text-slate-400"
                        )} />
                    </div>

                    {isDragActive ? (
                        <p className="text-main font-medium">Drop the file here...</p>
                    ) : (
                        <>
                            <p className="text-slate-900 font-medium mb-1">
                                Drag & drop your statement here
                            </p>
                            <p className="text-sm text-slate-500 mb-4">
                                or click to browse
                            </p>
                            <p className="text-xs text-slate-400">
                                PNG, JPEG, or WebP (max {maxSize / 1024 / 1024}MB)
                            </p>
                        </>
                    )}
                </div>
            </div>

            {/* Error message */}
            {error && (
                <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 rounded-lg">
                    <AlertCircle className="h-5 w-5 flex-shrink-0" />
                    <p className="text-sm">{error}</p>
                </div>
            )}

            {/* Selected file preview */}
            {selectedFile && !error && (
                <div className={cn(
                    "flex items-center justify-between p-4 rounded-lg border",
                    isUploading ? "bg-main3 border-main/30" : "bg-slate-50 border-slate-200"
                )}>
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white rounded-lg shadow-sm">
                            <FileText className="h-6 w-6 text-main" />
                        </div>
                        <div>
                            <p className="font-medium text-slate-900 truncate max-w-[200px] sm:max-w-none">
                                {selectedFile.name}
                            </p>
                            <p className="text-sm text-slate-500">
                                {formatFileSize(selectedFile.size)}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {isUploading ? (
                            <div className="flex items-center gap-2">
                                <div className="w-24 h-2 bg-main2 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-main rounded-full transition-all duration-300"
                                        style={{ width: `${uploadProgress}%` }}
                                    />
                                </div>
                                <span className="text-sm text-main font-medium">{uploadProgress}%</span>
                            </div>
                        ) : uploadProgress === 100 ? (
                            <CheckCircle className="h-6 w-6 text-progress-500" />
                        ) : (
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    removeFile();
                                }}
                                className="h-8 w-8"
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
