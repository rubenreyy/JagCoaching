// Revised on March 15 to Send Video to Backend
// Also to to send the file name to /process-audio/

import React, { useState } from 'react';

const Upload = ({ setCurrentPage, setFeedback }) => {
    const [files, setFiles] = useState([]);
    const [uploadProgress, setUploadProgress] = useState({});
    const [isProcessing, setIsProcessing] = useState(false);

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const uploadResponse = await fetch("http://localhost:8000/api/upload/", {
                method: "POST",
                body: formData,
            });
            
            const uploadData = await uploadResponse.json();
            console.log("Uploaded File:", uploadData);
            
            if (uploadData.filename) {
                processAudio(uploadData.filename);
            }
        } catch (error) {
            console.error("Upload failed:", error);
        }
    };

    const processAudio = async (fileName) => {
        setIsProcessing(true);
        try {
            const response = await fetch("http://localhost:8000/api/process-audio/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ file_name: fileName }),
            });
            
            const data = await response.json();
            console.log("AI Feedback:", data);
            
            setFeedback(data);  // Pass feedback to state for frontend display
            setCurrentPage("feedback"); // Navigate to feedback page
        } catch (error) {
            console.error("Processing failed:", error);
        }
        setIsProcessing(false);
    };

    return (
        <div className="upload-container">
            <h2>Upload Your Presentation</h2>
            <input
                type="file"
                onChange={handleFileChange}
                accept=".mp4,.mov,.avi,.webm,.pdf,.ppt,.pptx"
            />
            {isProcessing && <p>Processing video... Please wait.</p>}
        </div>
    );
};

export default Upload;
