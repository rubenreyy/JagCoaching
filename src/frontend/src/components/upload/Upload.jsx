// Revised on March 15 to Send Video to Backend
// Also to to send the file name to /process-audio/

import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import Feedback from '../feedback/Feedback';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Progress } from '../ui/Progress';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../ui/Accordion';
import { AlertCircle, CheckCircle2, File, Upload as UploadIcon, X } from 'lucide-react';
import AIAnalyzing from '../loading/AIAnalyzing';
import { mockFeedbackData } from '../../utils/mockFeedback.js';

const Upload = ({ setCurrentPage, setFeedbackData }) => {
    const [files, setFiles] = useState([]);
    const [uploadProgress, setUploadProgress] = useState({});
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [uploadedFileId, setUploadedFileId] = useState(null);
    const [isUploadComplete, setIsUploadComplete] = useState(false);
    const accessToken = localStorage.getItem("accessToken");
    
    console.log("Initial accessToken check:", accessToken);

    const handleFileChange = async (event) => {
        if (!event.target.files) return;
        const file = event.target.files[0];
        
        console.log("Starting file upload...");
        setIsUploadComplete(false); // Reset upload state
        
        // Clear previous upload state
        setFiles([file]);
        setUploadProgress({});
        setUploadedFileId(null);
        
        let progressInterval = null;
        try {
            // Start upload progress animation
            progressInterval = setInterval(() => {
                setUploadProgress(prev => {
                    const currentProgress = prev[file.name] || 0;
                    return currentProgress >= 90 ? prev : { 
                        ...prev, 
                        [file.name]: currentProgress + 10 
                    };
                });
            }, 500);

            const formData = new FormData();
            formData.append("file", file);

            const uploadResponse = await fetch("http://localhost:8000/api/videos/upload/", {
                method: "POST",
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: formData,
            });
            
            clearInterval(progressInterval);

            if (!uploadResponse.ok) {
                throw new Error('Upload failed');
            }

            const uploadData = await uploadResponse.json();
            console.log("Upload successful:", uploadData);
            
            // Set final upload state
            setUploadedFileId(uploadData.filename);
            setUploadProgress(prev => ({ ...prev, [file.name]: 100 }));
            setIsUploadComplete(true);

        } catch (error) {
            console.error("Upload failed:", error);
            if (progressInterval) clearInterval(progressInterval);
            setFiles([]);
            setUploadProgress({});
            setIsUploadComplete(false);
            alert(`Upload failed: ${error.message}`);
        }
    };

    const removeFile = (fileName) => {
        console.log("Removing file:", fileName);
        setFiles((prevFiles) => prevFiles.filter((file) => file.name !== fileName));
        setUploadProgress((prev) => {
            const newProgress = { ...prev };
            delete newProgress[fileName];
            return newProgress;
        });
    };

    const handleAnalyze = async () => {
        if (!uploadedFileId || !isUploadComplete) {
            console.error("Cannot analyze: No file uploaded or upload not complete");
            return;
        }

        setIsAnalyzing(true);
        
        // Set to false to use real data
        const USE_MOCK_DATA = false;
        
        try {
            if (USE_MOCK_DATA) {
                console.log("Using mock data for testing");
                setTimeout(() => {
                    setFeedbackData(mockFeedbackData);
                    setIsAnalyzing(false);
                    setCurrentPage('feedback');
                }, 3000);
                return;
            }

            console.log("Starting analysis for file:", uploadedFileId);
            const response = await fetch("http://localhost:8000/api/videos/process-audio/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${accessToken}`,
                },
                body: JSON.stringify({ file_name: uploadedFileId }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Processing failed');
            }

            const analysisData = await response.json();
            console.log("Analysis data received:", analysisData);
            setFeedbackData(analysisData);
            setCurrentPage('feedback');
        } catch (error) {
            console.error("Analysis failed:", error);
            alert(`Analysis failed: ${error.message}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    if (!accessToken) {
        return (
            <div className="upload-container">
                <h2>Please Log In</h2>
                <p>You must be logged in to upload files.</p>
                <button onClick={() => setCurrentPage("login")}>Go to Login</button>
            </div>
        );
    }

    return (
        <>
            {isAnalyzing && <AIAnalyzing />}
            <div className="max-w-[1280px] mx-auto py-20 flex flex-col gap-7">
                <Card>
                    <CardHeader>
                        <CardTitle>Upload Your Presentation</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="border-2 border-dashed border-[#EEEEEE] rounded-2xl p-12 text-center">
                            <UploadIcon className="mx-auto h-12 w-12 text-[#8E8E8E]" />
                            <p className="mt-2 text-xl font-mono text-[#030303]">
                                Drag and drop your files here, or
                            </p>
                            <label
                                htmlFor="file-upload"
                                className="mt-4 cursor-pointer inline-flex items-center px-8 py-3 text-white bg-[#030303] rounded-full font-mono font-semibold hover:bg-primary transition-colors"
                            >
                                Browse Files
                            </label>
                            <input
                                id="file-upload"
                                name="file-upload"
                                type="file"
                                className="sr-only"
                                onChange={handleFileChange}
                                accept=".mp4,.mov,.avi"
                            />
                            <p className="mt-4 text-sm font-mono text-[#8E8E8E]">
                                Supported formats: .mp4, .mov, .avi (Max 500MB)
                            </p>
                        </div>
                    </CardContent>
                </Card>

                {files.length > 0 && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Uploaded Files</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="divide-y divide-[#EEEEEE]">
                                {files.map((file, index) => (
                                    <li key={index} className="py-4 flex items-center justify-between">
                                        <div className="flex items-center">
                                            <File className="h-5 w-5 text-[#8E8E8E] mr-3" />
                                            <span className="text-lg font-mono text-[#030303]">{file.name}</span>
                                        </div>
                                        <div className="flex items-center">
                                            {uploadProgress[file.name] === 100 ? (
                                                <CheckCircle2 className="h-5 w-5 text-primary mr-2" />
                                            ) : (
                                                <Progress value={uploadProgress[file.name]} className="w-24 mr-2" />
                                            )}
                                            <button 
                                                onClick={() => removeFile(file.name)}
                                                className="p-1 hover:text-primary transition-colors"
                                            >
                                                <X className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                )}

                <div className="relative group">
                    <button 
                        onClick={handleAnalyze}
                        className={`w-full px-8 py-3 rounded-full font-mono font-semibold transition-colors
                            ${isUploadComplete
                                ? 'bg-[#030303] text-white hover:bg-primary'
                                : 'bg-[#EEEEEE] text-[#8E8E8E] cursor-not-allowed'
                            }`}
                        disabled={!isUploadComplete}
                    >
                        {isAnalyzing ? "Processing..." : "Analyze My Presentation"}
                    </button>
                </div>

                <Card>
                    <CardContent className="p-0">
                        <Accordion type="single" collapsible>
                            <AccordionItem value="guidelines">
                                <AccordionTrigger>Upload Guidelines & Help</AccordionTrigger>
                                <AccordionContent>
                                    <ul className="list-disc list-inside space-y-2 font-mono text-[#030303]">
                                        <li>Supported file formats: .mp4, .mov, .avi</li>
                                        <li>Maximum file size: 500MB per file</li>
                                        <li>For best results, ensure your video has clear audio</li>
                                        <li>If your file fails to upload, try reducing its size or using a different format</li>
                                    </ul>
                                    <button className="mt-6 px-6 py-2 border-2 border-[#EEEEEE] rounded-full font-mono font-semibold text-[#030303] hover:bg-primary hover:text-white hover:border-primary transition-colors flex items-center">
                                        <AlertCircle className="mr-2 h-4 w-4" />
                                        Contact Support
                                    </button>
                                </AccordionContent>
                            </AccordionItem>
                        </Accordion>
                    </CardContent>
                </Card>
            </div>
        </>
    );
};

Upload.propTypes = {
    setCurrentPage: PropTypes.func.isRequired,
    setFeedbackData: PropTypes.func.isRequired,
};

export default Upload;
