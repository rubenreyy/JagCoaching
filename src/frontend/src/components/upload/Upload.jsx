// Revised on March 15 to Send Video to Backend
// Also to to send the file name to /process-audio/

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import Feedback from '../feedback/Feedback';



const Upload = ({ setCurrentPage  }) => {
    const [files, setFiles] = useState([]);
    const [uploadProgress, setUploadProgress] = useState({});
    const [isProcessing, setIsProcessing] = useState(false);
    const [feedbackData, setFeedbackData] = useState({});
    const [feedback, setFeedback] = useState(null);
    const accessToken = localStorage.getItem("accessToken");
    console.log("accessToken",accessToken)
    // useEffect(() => {
    //     if (Object.keys(feedbackData).length > 0) {
    //         // When feedback data is available, redirect to feedback page
    //         console.log("Feedback data is available");
    //         setFeedback(<Feedback feedback={feedbackData} />);
    //         setCurrentPage("feedback",feedback);
    //     }
    // }, [feedbackData, setCurrentPage]);
    
    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const uploadResponse = await fetch("http://localhost:8000/api/videos/upload/", {
                method: "POST",
                headers: { 
                    "Access-Control-Allow-Origin": "http://localhost:3000",
                    "Authorization": `Bearer ${accessToken}`
                },
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
            const response = await fetch("http://localhost:8000/api/videos/process-audio/", {
                method: "POST",
                body: JSON.stringify({ file_name: fileName }),
                headers: { "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Access-Control-Allow-Origin": "http://localhost:3000",
                            "Access-Control-Allow-Headers": "*",

                },

            }).then(response => {
                return response.json();
            })
            
            const data = await response;
            console.log("AI Feedback:", data.feedback);
            setFeedbackData(data.feedback);
            setFeedback(<Feedback feedback={data.feedback} />);
            
        } catch (error) {
            console.error("Processing failed:", error);
        }
        finally {
            setIsProcessing(false);
        }
    };

    useEffect(() => {
        if (Object.keys(feedbackData).length > 0) {
            // When feedback data is available, redirect to feedback page
            console.log("Feedback data is available");
            setFeedback(<Feedback feedback={feedbackData} />);
        }
    }, [feedbackData]);

    return (
        <div className="upload-container">
            <h2>Upload Your Presentation</h2>
            <input
                type="file"
                onChange={handleFileChange}
                accept=".mp4,.mov,.avi,.webm,.pdf,.ppt,.pptx"
            />
            <br />
            {isProcessing && <p>Processing video... Please wait.</p>}
            {Object.keys(feedbackData).length > 0 && (
                <>
                    <p>Video processed! Redirecting to feedback...</p>
                    <Feedback feedback={feedbackData} />
                </>
            )}
        </div>
    );
};

Upload.propTypes = {
    setCurrentPage: PropTypes.func.isRequired,
    // setFeedback: PropTypes.func.isRequired
};

export default Upload;
