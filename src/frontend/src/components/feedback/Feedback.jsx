// Revised on March 15 to show AI-generated insights

import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Progress } from '../ui/Progress'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Download, FileText, Video } from 'lucide-react'

const FeedbackChart = ({ data, title, suggestions, details }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column - Chart */}
          <div>
            <h3 className="text-lg font-semibold font-mono mb-4">Metrics</h3>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="score" fill="#0500FF" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Right Column - Details and Suggestions */}
          <div className="space-y-6">
            {/* Detailed Metrics */}
            <div>
              <h3 className="text-lg font-semibold font-mono mb-4">Details</h3>
              <div className="space-y-4">
                {details.map((detail, index) => (
                  <div key={index} className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">{detail.title}</h4>
                    {detail.type === 'list' ? (
                      <ul className="list-disc list-inside space-y-1">
                        {detail.content.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p>{detail.content}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Suggestions */}
            <div>
              <h3 className="text-lg font-semibold font-mono mb-4">Suggestions</h3>
              <ul className="space-y-2 font-mono text-[#030303]">
                {suggestions.map((suggestion, index) => (
                  <li key={index} className="bg-blue-50 p-3 rounded-lg">
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

const AudioAnalysis = ({ feedbackData }) => (
  <div className="space-y-4">
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="font-semibold mb-2">Speaking Pace</h3>
      <p>{feedbackData.speech_rate.wpm} WPM - {feedbackData.speech_rate.assessment}</p>
      <p className="text-gray-600 mt-1">{feedbackData.speech_rate.suggestion}</p>
    </div>
    
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="font-semibold mb-2">Filler Words</h3>
      <div className="flex gap-2 flex-wrap mb-2">
        {Object.entries(feedbackData.filler_words.counts).map(([word, count]) => (
          <span key={word} className="px-2 py-1 bg-gray-200 rounded">
            {word}: {count}x
          </span>
        ))}
      </div>
      <p className="text-gray-600">{feedbackData.filler_words.suggestion}</p>
    </div>
    
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="font-semibold mb-2">Clarity</h3>
      <p>{feedbackData.clarity.score}% - {feedbackData.clarity.suggestion}</p>
    </div>
  </div>
);

const LanguageAnalysis = ({ feedbackData }) => (
  <div className="space-y-4">
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="font-semibold mb-2">Sentiment Analysis</h3>
      <p>{feedbackData.sentiment.label} (Confidence: {Math.round(feedbackData.sentiment.score * 100)}%)</p>
      <p className="text-gray-600 mt-1">{feedbackData.sentiment.suggestion}</p>
    </div>
    
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="font-semibold mb-2">Key Topics</h3>
      <div className="flex gap-2 flex-wrap mb-2">
        {feedbackData.keywords.topics.map((topic) => (
          <span key={topic} className="px-2 py-1 bg-blue-100 rounded">{topic}</span>
        ))}
      </div>
      <p className="text-gray-600">{feedbackData.keywords.context}</p>
    </div>
  </div>
);

// New component for PowerPoint feedback
const PresentationAnalysis = ({ feedbackData }) => (
  <div className="space-y-6">
    <div className="p-6 bg-white rounded-lg shadow-sm">
      <h3 className="text-xl font-semibold mb-4">Slide Content Clarity</h3>
      <p className="text-gray-800 mb-4">{feedbackData.slide_clarity}</p>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div className="bg-primary h-2.5 rounded-full" style={{ width: '85%' }}></div>
      </div>
    </div>
    
    <div className="p-6 bg-white rounded-lg shadow-sm">
      <h3 className="text-xl font-semibold mb-4">Visual Design Quality</h3>
      <p className="text-gray-800 mb-4">{feedbackData.visual_quality}</p>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div className="bg-primary h-2.5 rounded-full" style={{ width: '75%' }}></div>
      </div>
    </div>
    
    <div className="p-6 bg-white rounded-lg shadow-sm">
      <h3 className="text-xl font-semibold mb-4">Key Topics & Themes</h3>
      <p className="text-gray-800">{feedbackData.key_topics}</p>
    </div>
    
    <div className="p-6 bg-white rounded-lg shadow-sm border-l-4 border-primary">
      <h3 className="text-xl font-semibold mb-2">Improvement Suggestion</h3>
      <p className="text-gray-800">{feedbackData.overall_suggestion}</p>
    </div>
  </div>
);

const Feedback = ({ feedbackData, setCurrentPage }) => {
  const [performanceData, setPerformanceData] = useState([])
  const [languageData, setLanguageData] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [feedbackType, setFeedbackType] = useState('video') // 'video' or 'presentation'

  useEffect(() => {
    // If feedbackData is provided directly, use it
    if (feedbackData) {
      // Check if this is presentation feedback
      if (feedbackData.feedback_type === 'presentation') {
        setFeedbackType('presentation')
      } else {
        setFeedbackType('video')
        processFeedbackData(feedbackData)
      }
      return
    }
    
    // Otherwise, check if we need to load a specific presentation
    const presentationId = localStorage.getItem("currentPresentationId")
    if (presentationId) {
      fetchPresentationData(presentationId)
    }
  }, [feedbackData])
  
  const fetchPresentationData = async (presentationId) => {
    try {
      setIsLoading(true)
      const accessToken = localStorage.getItem("accessToken")
      
      if (!accessToken) {
        setError("You must be logged in to view feedback")
        setIsLoading(false)
        return
      }
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/videos/presentations/${presentationId}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch presentation data')
      }
      
      const data = await response.json()
      console.log("Fetched presentation:", data)
      
      // Process the feedback data
      processFeedbackData(data.feedback_data)
      
    } catch (err) {
      console.error("Error fetching presentation:", err)
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }
  
  const processFeedbackData = (data) => {
    console.log("Processing feedback data:", data)
    
    // Process audio/performance data with null checks
    setPerformanceData([
      { 
        name: "Speech Rate", 
        score: data.speech_rate?.wpm || 0 
      },
      { 
        name: "Clarity", 
        score: data.clarity?.score || 0 
      },
      { 
        name: "Pauses", 
        score: data.pauses?.count || 0 
      },
      { 
        name: "Filler Words", 
        score: data.filler_words?.total || 0 
      }
    ])
    
    // Process language data
    setLanguageData([
      { 
        name: "Sentiment", 
        score: data.sentiment?.score ? data.sentiment.score * 100 : 0 
      },
      { 
        name: "Grammar", 
        score: data.grammar?.score || 0 
      },
      { 
        name: "Vocabulary", 
        score: data.vocabulary?.score || 0 
      },
      { 
        name: "Engagement", 
        score: data.engagement?.score || 0 
      }
    ])
  }
  
  // Navigation handler function
  const navigateTo = (page) => {
    console.log(`Navigating to ${page} page`);
    if (typeof setCurrentPage === 'function') {
      setCurrentPage(page);
    } else {
      console.error("setCurrentPage is not available, using direct navigation");
      // Fallback to direct URL navigation
      window.location.href = `/${page}`;
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p className="text-lg font-mono">Loading feedback data...</p>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-screen gap-4">
        <p className="text-lg font-mono text-red-500">{error}</p>
        <button 
          onClick={() => navigateTo("upload")}
          className="px-6 py-2 bg-black text-white rounded-full font-mono"
        >
          Try Again
        </button>
      </div>
    )
  }
  
  // If no data is available, show a more helpful message with guidance
  if ((!feedbackData && performanceData.length === 0) || 
      (feedbackType === 'presentation' && !feedbackData)) {
    return (
      <div className="flex flex-col justify-center items-center h-screen gap-6 max-w-md mx-auto text-center px-4">
        <div className="bg-gray-100 p-8 rounded-lg shadow-sm w-full">
          <h2 className="text-2xl font-bold font-mono mb-4">No Feedback Data Available</h2>
          
          <p className="font-mono text-[#030303] mb-6">
            To get personalized feedback on your presentation skills:
          </p>
          
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-md border border-gray-200">
              <h3 className="font-semibold mb-2">Upload a Presentation</h3>
              <p className="text-gray-700 mb-3">Record or upload a video of your presentation for AI analysis.</p>
              <button 
                onClick={() => navigateTo("upload")}
                className="px-4 py-2 bg-primary text-white rounded-md font-mono 
                  hover:bg-blue-700 hover:shadow-md transform hover:-translate-y-0.5 
                  transition-all duration-200 ease-in-out w-full"
              >
                Go to Upload Page
              </button>
            </div>
            
            <div className="bg-white p-4 rounded-md border border-gray-200">
              <h3 className="font-semibold mb-2">View Past Presentations</h3>
              <p className="text-gray-700 mb-3">Check your progress and review feedback from previous presentations.</p>
              <button 
                onClick={() => navigateTo("progress")}
                className="px-4 py-2 bg-black text-white rounded-md font-mono 
                  hover:bg-gray-800 hover:shadow-md transform hover:-translate-y-0.5 
                  transition-all duration-200 ease-in-out w-full"
              >
                Go to Progress Page
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // PowerPoint presentation feedback display
  if (feedbackType === 'presentation') {
    return (
      <div className="max-w-[1280px] mx-auto px-4 py-8">
        {/* Presentation Summary Card */}
        <Card className="mb-8">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>PowerPoint Analysis</CardTitle>
              <p className="text-sm text-gray-500 mt-1">Analyzed on {new Date().toLocaleDateString()}</p>
            </div>
            <FileText className="h-10 w-10 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center mb-6">
              <div className="text-4xl font-bold font-mono text-primary mr-4">
                Summary
              </div>
            </div>
            <p className="font-mono text-[#030303] mb-4">
              {feedbackData.overall_suggestion}
            </p>
            <button className="px-6 py-2 bg-black text-white rounded-full font-mono font-semibold hover:bg-primary transition-colors flex items-center">
              <Download className="mr-2 h-4 w-4" /> Download Analysis
            </button>
          </CardContent>
        </Card>

        {/* PowerPoint Analysis Content */}
        <PresentationAnalysis feedbackData={feedbackData} />
      </div>
    )
  }

  // Video feedback display (existing code)
  // Format filler words for display
  const fillerWordsList = Object.entries(feedbackData.filler_words?.counts || {})
    .map(([word, count]) => `"${word}": ${count} times`)

  return (
    <div className="max-w-[1280px] mx-auto px-4 py-8">
      {/* Presentation Summary Card */}
      <Card className="mb-8">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Video Presentation Analysis</CardTitle>
            <p className="text-sm text-gray-500 mt-1">Analyzed on {new Date().toLocaleDateString()}</p>
          </div>
          <Video className="h-10 w-10 text-primary" />
        </CardHeader>
        <CardContent>
          <h2 className="text-2xl font-bold font-mono mb-2">Speech Analysis Results</h2>
          <div className="flex items-center mb-4">
            <div className="text-4xl font-bold font-mono text-primary mr-4">
              {Math.round(feedbackData.clarity?.score || 0)}%
            </div>
            <div className="text-lg font-mono">Overall Clarity Score</div>
          </div>
          <p className="font-mono text-[#030303]">
            {feedbackData.clarity?.suggestion}
          </p>
        </CardContent>
      </Card>

      {/* Feedback Tabs - Only for video feedback */}
      <Tabs defaultValue="audio" className="mb-8">
        <TabsList>
          <TabsTrigger value="audio">Audio</TabsTrigger>
          <TabsTrigger value="language">Language</TabsTrigger>
        </TabsList>

        <TabsContent value="audio">
          <FeedbackChart
            data={performanceData}
            title="Audio Analysis"
            details={[
              {
                title: "Speaking Pace",
                content: `${feedbackData.speech_rate?.wpm} WPM - ${feedbackData.speech_rate?.assessment}`
              },
              {
                title: "Clarity Score",
                content: `${feedbackData.clarity?.score}% - Excellent clarity`
              },
              {
                title: "Filler Words",
                type: 'list',
                content: fillerWordsList
              }
            ]}
            suggestions={[
              feedbackData.speech_rate?.suggestion,
              feedbackData.clarity?.suggestion,
              feedbackData.filler_words?.suggestion
            ].filter(Boolean)}
          />
        </TabsContent>

        <TabsContent value="language">
          <FeedbackChart
            data={languageData}
            title="Language Analysis"
            details={[
              {
                title: "Sentiment Analysis",
                content: `${feedbackData.sentiment?.label} (${Math.round(feedbackData.sentiment?.score * 100)}%)`
              },
              {
                title: "Key Topics",
                type: 'list',
                content: feedbackData.keywords?.topics || []
              }
            ]}
            suggestions={[
              feedbackData.sentiment?.suggestion,
              feedbackData.keywords?.context
            ].filter(Boolean)}
          />
        </TabsContent>
      </Tabs>

      {/* Report Card */}
      <Card>
        <CardHeader>
          <CardTitle>Detailed Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center mb-6">
            <button className="px-6 py-2 bg-black text-white rounded-full font-mono font-semibold hover:bg-primary transition-colors flex items-center">
              <Download className="mr-2 h-4 w-4" /> Download Full Report
            </button>
          </div>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold font-mono mb-2">Key Metrics</h3>
              <ul className="list-disc list-inside font-mono text-[#030303]">
                <li>Speaking Rate: {feedbackData.speech_rate?.wpm} WPM</li>
                <li>Clarity Score: {feedbackData.clarity?.score}%</li>
                <li>Sentiment: {feedbackData.sentiment?.label}</li>
                <li>Key Topics: {feedbackData.keywords?.topics?.join(', ')}</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Feedback
