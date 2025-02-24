import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Progress } from '../ui/Progress'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Download } from 'lucide-react'

// Add console log to verify component mounting
console.log('Feedback component rendering')

// Mock data for the charts
const audioData = [
  { name: "Clarity", score: 85 },
  { name: "Pace", score: 70 },
  { name: "Fillers", score: 60 },
  { name: "Pronunciation", score: 90 },
]

const visualData = [
  { name: "Engagement", score: 80 },
  { name: "Eye Contact", score: 75 },
  { name: "Body Language", score: 65 },
]

const languageData = [
  { name: "Grammar", score: 95 },
  { name: "Coherence", score: 85 },
  { name: "Persuasiveness", score: 80 },
]

const slideData = [
  { name: "Readability", score: 90 },
  { name: "Balance", score: 75 },
  { name: "Visual Appeal", score: 85 },
]

const FeedbackChart = ({ data, title, suggestions }) => {
  // Add console log to verify chart rendering
  console.log('FeedbackChart rendering:', title)
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold font-mono mb-4">Scores</h3>
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
          <div>
            <h3 className="text-lg font-semibold font-mono mb-4">Suggestions</h3>
            <ul className="space-y-2 font-mono text-[#030303]">
              {suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

const Feedback = () => {
  // Add error boundary
  try {
    return (
      <div className="max-w-[1280px] mx-auto px-4 py-8">
        {/* Presentation Summary Card */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Presentation Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <h2 className="text-2xl font-bold font-mono mb-2">Midterm Project Presentation</h2>
            <p className="font-mono text-[#8E8E8E] mb-4">Uploaded on March 15, 2025 at 2:30 PM</p>
            <div className="flex items-center mb-4">
              <div className="text-4xl font-bold font-mono text-primary mr-4">85%</div>
              <div className="text-lg font-mono">Strong Presentation!</div>
            </div>
            <p className="font-mono text-[#030303]">
              Good eye contact and engaging content, but pacing needs improvement. Focus on slowing down your speech and
              reducing filler words for a more polished delivery.
            </p>
          </CardContent>
        </Card>

        {/* Feedback Tabs */}
        <Tabs defaultValue="audio" className="mb-8">
          <TabsList>
            <TabsTrigger value="audio">Audio</TabsTrigger>
            <TabsTrigger value="visual">Visual</TabsTrigger>
            <TabsTrigger value="language">Language</TabsTrigger>
            <TabsTrigger value="slides">Slides</TabsTrigger>
          </TabsList>

          <TabsContent value="audio">
            <FeedbackChart
              data={audioData}
              title="Audio Feedback"
              suggestions={[
                "Reduce speaking pace by about 10%",
                'Work on eliminating filler words like "um" and "uh"',
                "Practice enunciating challenging words"
              ]}
            />
          </TabsContent>

          <TabsContent value="visual">
            <FeedbackChart
              data={visualData}
              title="Visual Feedback"
              suggestions={[
                "Maintain more consistent eye contact with the audience",
                "Use more hand gestures to emphasize key points",
                "Work on varying your facial expressions to show enthusiasm"
              ]}
            />
          </TabsContent>

          <TabsContent value="language">
            <FeedbackChart
              data={languageData}
              title="Language & Content Feedback"
              suggestions={[
                "Use more transition phrases to improve coherence",
                "Incorporate more persuasive language techniques",
                "Reduce repetition of certain phrases"
              ]}
            />
          </TabsContent>

          <TabsContent value="slides">
            <FeedbackChart
              data={slideData}
              title="Slide Quality Feedback"
              suggestions={[
                "Reduce text on slides 3, 7, and 12",
                "Add more visual elements to support key points",
                "Use a consistent color scheme across all slides"
              ]}
            />
          </TabsContent>
        </Tabs>

        {/* Report & Comparison Card */}
        <Card>
          <CardHeader>
            <CardTitle>Report & Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center mb-6">
              <button className="px-6 py-2 bg-black text-white rounded-full font-mono font-semibold hover:bg-primary transition-colors flex items-center">
                <Download className="mr-2 h-4 w-4" /> Download Full Report
              </button>
              <div className="flex items-center font-mono">
                <span className="mr-2">Compare with:</span>
                <select className="border rounded-lg p-2">
                  <option>Previous Presentation</option>
                  <option>Two Presentations Ago</option>
                  <option>First Presentation</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-lg font-semibold font-mono mb-2">Current Presentation</h3>
                <Progress value={85} className="mb-2" />
                <span className="text-sm font-mono text-[#8E8E8E]">85% Overall Score</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold font-mono mb-2">Previous Presentation</h3>
                <Progress value={75} className="mb-2" />
                <span className="text-sm font-mono text-[#8E8E8E]">75% Overall Score</span>
              </div>
            </div>
            <div className="mt-6">
              <h3 className="text-lg font-semibold font-mono mb-2">Improvement Areas</h3>
              <ul className="list-disc list-inside font-mono text-[#030303]">
                <li>10% improvement in overall score</li>
                <li>Significant progress in slide quality</li>
                <li>Slight decrease in speaking pace, which is positive</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  } catch (error) {
    console.error('Error in Feedback component:', error)
    return (
      <div className="max-w-[1280px] mx-auto px-4 py-8">
        <Card>
          <CardContent>
            <h2 className="text-2xl font-bold font-mono text-red-500">
              Error loading feedback page. Please try again.
            </h2>
          </CardContent>
        </Card>
      </div>
    )
  }
}

export default Feedback 