// Revised on March 15 to Send Video to Backend
// Also to to send the file name to /process-audio/

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import Feedback from '../feedback/Feedback';
import {feedback} from '../feedback/Feedback';


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
                console.log(uploadData.filename)
                processAudio(uploadData.filename);
            }
        } catch (error) {
            console.error("Upload failed:", error);
        }
    };

    const processAudio = async (fileName) => {
        setIsProcessing(true);
        try {
            console.log(JSON.stringify({ file_name: fileName }))
            console.log(fileName)
            const response = await fetch("http://localhost:8000/api/process-audio/", {
                method: "POST",
                body: JSON.stringify({ file_name: fileName }),
                headers: { "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Access-Control-Allow-Origin": "http://localhost:3000",
                            "Access-Control-Allow-Headers": "*",

                },

            });
            
            const data = await response.json();
            console.log("AI Feedback:", data);
            
            
            Feedback({ feedback: data.feedback });
            feedback(data.feedback);
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

// Upload.propTypes = {
//     setCurrentPage: PropTypes.func.isRequired,
//     setFeedback: PropTypes.func.isRequired
// };

export default Upload;
