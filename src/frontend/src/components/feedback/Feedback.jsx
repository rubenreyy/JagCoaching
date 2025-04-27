// Revised on March 15 to show AI-generated insights

import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Progress } from '../ui/Progress'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Download } from 'lucide-react'

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

const Feedback = ({ feedbackData }) => {
  const [performanceData, setPerformanceData] = useState([])
  const [languageData, setLanguageData] = useState([])

  useEffect(() => {
    if (feedbackData) {
      console.log("Processing feedback data:", feedbackData)
      
      // Process audio/performance data with null checks
      setPerformanceData([
        { 
          name: "Speech Rate", 
          score: feedbackData.speech_rate?.wpm || 0 
        },
        { 
          name: "Clarity", 
          score: feedbackData.clarity?.score || 0 
        },
        { 
          name: "Filler Words", 
          score: 100 - ((feedbackData.filler_words?.total || 0) * 10) 
        }
      ])

      // Process language data with null checks
      setLanguageData([
        { 
          name: "Sentiment", 
          score: Math.round((feedbackData.sentiment?.score || 0) * 100) 
        },
        { 
          name: "Topic Coverage", 
          score: (feedbackData.keywords?.topics?.length || 0) * 20 
        }
      ])
    }
  }, [feedbackData])

  if (!feedbackData) {
    return <div>Loading feedback data...</div>
  }

  // Format filler words for display
  const fillerWordsList = Object.entries(feedbackData.filler_words?.counts || {})
    .map(([word, count]) => `"${word}": ${count} times`)

  return (
    <div className="max-w-[1280px] mx-auto px-4 py-8">
      {/* Presentation Summary Card */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Presentation Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <h2 className="text-2xl font-bold font-mono mb-2">Speech Analysis Results</h2>
          <p className="font-mono text-[#8E8E8E] mb-4">
            Analyzed on {new Date().toLocaleDateString()}
          </p>
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

      {/* Feedback Tabs */}
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
