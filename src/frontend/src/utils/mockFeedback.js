export const mockFeedbackData = {
    transcript: "Hi Amanda, I know you had a couple of questions...",
    sentiment: {
        label: "Neutral",
        score: 0.53,
        suggestion: "Your tone is well-balanced and professional."
    },
    filler_words: {
        counts: {
            "like": 1,
            "so": 7
        },
        total: 8,
        suggestion: "Try to reduce filler words by pausing briefly instead."
    },
    speech_rate: {
        wpm: 120.13,
        assessment: "optimal",
        suggestion: "Your speaking pace is ideal for clear communication."
    },
    keywords: {
        topics: [
            "allocation cake",
            "cakes multiply",
            "cost labor",
            "cost sponge",
            "total cakes"
        ],
        context: "These key topics represent the main themes discussed in your presentation."
    },
    clarity: {
        score: 99.03,
        suggestion: "Excellent clarity! Your speech is very well articulated."
    }
} 