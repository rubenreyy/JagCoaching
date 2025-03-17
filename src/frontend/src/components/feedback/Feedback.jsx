// Revised on March 15 to show AI-generated insights

import React from 'react';
import PropTypes from 'prop-types';

const Feedback = ({ feedback }) => {
    if (!feedback) {
        return <p>No feedback available. Please upload and process a video.</p>;
    }

    return (
        <div className="feedback-container">
            <h2>Speech Analysis Report</h2>
            <p><strong>Transcript:</strong> {feedback.transcript}</p>
            <p><strong>Sentiment:</strong> {feedback.sentiment[0].label} ({feedback.sentiment[0].score.toFixed(2)})</p>
            <p><strong>Filler Words:</strong> {JSON.stringify(feedback.filler_words)}</p>
            <p><strong>Speech Rate (WPM):</strong> {feedback.wpm}</p>
            <p><strong>Pronunciation Clarity:</strong> {feedback.clarity}%</p>
            <p><strong>Key Topics:</strong> {feedback.keywords.join(", ")}</p>
        </div>
    );
};

Feedback.propTypes = {
    feedback: PropTypes.object
};

export default Feedback;
