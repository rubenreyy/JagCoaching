import { useState } from 'react'
import { Button } from "../../components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/Card"
import { Progress } from "../../components/ui/Progress"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/Table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/Select"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts"
import { ArrowUpRight, Eye } from "lucide-react"
import { Tabs } from "../../components/ui/Tabs"
import { Accordion } from "../../components/ui/Accordion"

// Mock data with consistent date format
const overallProgressData = [
  { date: "Jan 2025", score: 65 },
  { date: "Feb 2025", score: 70 },
  { date: "Mar 2025", score: 75 },
  { date: "Apr 2025", score: 80 },
  { date: "May 2025", score: 85 },
]

const skillsData = [
  { name: "Speaking Pace", score: 80 },
  { name: "Vocal Clarity", score: 85 },
  { name: "Eye Contact", score: 75 },
  { name: "Grammar", score: 90 },
  { name: "Slide Design", score: 70 },
]

const pastPresentations = [
  { date: "May 1, 2025", title: "Research Talk", score: 85, summary: "Good eye contact, slow pacing" },
  { date: "Apr 15, 2025", title: "Project Pitch", score: 78, summary: "Lacked clarity, strong visuals" },
  { date: "Mar 30, 2025", title: "Class Debate", score: 92, summary: "Excellent speaking pace" },
  { date: "Mar 15, 2025", title: "Team Presentation", score: 88, summary: "Great slides, needs more engagement" },
  { date: "Mar 1, 2025", title: "Conference Talk", score: 82, summary: "Improved clarity, work on pacing" },
]

export default function ProgressPage({ setCurrentPage }) {
  const [dateFilter, setDateFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date-desc')

  // Filter and sort presentations
  const filteredPresentations = pastPresentations
    .filter(presentation => {
      if (dateFilter === 'all') return true
      const presentationDate = new Date(presentation.date)
      const today = new Date()
      const daysDiff = (today - presentationDate) / (1000 * 60 * 60 * 24)
      return daysDiff <= parseInt(dateFilter)
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date-desc':
          return new Date(b.date) - new Date(a.date)
        case 'date-asc':
          return new Date(a.date) - new Date(b.date)
        case 'score-desc':
          return b.score - a.score
        case 'score-asc':
          return a.score - b.score
        default:
          return 0
      }
    })

  return (
    <div className="max-w-[1280px] mx-auto py-8 px-4">
      <Card className="mb-8">
        <div className="p-6">
          <h2 className="text-2xl font-bold font-mono">Performance Overview</h2>
        </div>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h3 className="text-lg font-semibold font-mono mb-2">Total Presentations</h3>
              <p className="text-3xl font-bold font-mono">8</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold font-mono mb-2">Overall Improvement</h3>
              <p className="text-3xl font-bold font-mono text-primary">+15%</p>
            </div>
            <div>
              <h3 className="text-lg font-semibold font-mono mb-2">Best Score</h3>
              <p className="text-3xl font-bold font-mono">92%</p>
            </div>
          </div>
          <div className="mt-6">
            <h3 className="text-lg font-semibold font-mono mb-2">Key Takeaways</h3>
            <p className="font-mono text-[#030303]">
              Your presentation skills have shown consistent improvement. Focus on maintaining a steady speaking pace
              and enhancing slide design for even better results.
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="font-mono">Overall Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={overallProgressData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#0500FF" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-mono">Skills Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={skillsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#0500FF" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Past Presentation History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center mb-4">
            <Select value={dateFilter} onChange={setDateFilter}>
              <SelectTrigger className="w-[180px] font-mono">
                <SelectValue placeholder="Filter by date" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All time</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
                <SelectItem value="90">Last 90 days</SelectItem>
                <SelectItem value="180">Last 6 months</SelectItem>
                <SelectItem value="365">Last year</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onChange={setSortBy}>
              <SelectTrigger className="w-[180px] font-mono">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date-desc">Date (Newest first)</SelectItem>
                <SelectItem value="date-asc">Date (Oldest first)</SelectItem>
                <SelectItem value="score-desc">Score (Highest first)</SelectItem>
                <SelectItem value="score-asc">Score (Lowest first)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="font-mono">Date</TableHead>
                <TableHead className="font-mono">Presentation Title</TableHead>
                <TableHead className="font-mono">AI Score</TableHead>
                <TableHead className="font-mono">Summary</TableHead>
                <TableHead className="font-mono">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPresentations.map((presentation, index) => (
                <TableRow key={index}>
                  <TableCell className="font-mono">{presentation.date}</TableCell>
                  <TableCell className="font-mono">{presentation.title}</TableCell>
                  <TableCell className="font-mono">{presentation.score}%</TableCell>
                  <TableCell className="font-mono">{presentation.summary}</TableCell>
                  <TableCell>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      className="font-mono hover:bg-primary hover:text-white"
                      onClick={() => setCurrentPage('feedback')}
                    >
                      <Eye className="mr-2 h-4 w-4" /> View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-mono">Goals & AI Suggestions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold font-mono mb-4">Your Goals</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-mono">Improve speaking pace</span>
                    <span className="text-sm text-[#8E8E8E] font-mono">80% complete</span>
                  </div>
                  <Progress value={80} className="bg-[#EEEEEE]" />
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-mono">Reduce filler words</span>
                    <span className="text-sm text-[#8E8E8E] font-mono">60% complete</span>
                  </div>
                  <Progress value={60} className="bg-[#EEEEEE]" />
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold font-mono mb-4">AI Recommendations</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <ArrowUpRight className="mr-2 h-5 w-5 text-primary flex-shrink-0" />
                  <span className="font-mono text-[#030303]">Practice pacing with a metronome for 10 minutes daily.</span>
                </li>
                <li className="flex items-start">
                  <ArrowUpRight className="mr-2 h-5 w-5 text-primary flex-shrink-0" />
                  <span className="font-mono text-[#030303]">Use more pauses between key points for better clarity.</span>
                </li>
                <li className="flex items-start">
                  <ArrowUpRight className="mr-2 h-5 w-5 text-primary flex-shrink-0" />
                  <span className="font-mono text-[#030303]">Focus on maintaining steady eye contact with your audience.</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 