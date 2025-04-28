import { useState, useEffect } from 'react'
import { Button } from "../../components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/Card"
import { Progress } from "../../components/ui/Progress"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/Table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/Select"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts"
import { ArrowUpRight, Eye, FileText, Video } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/Tabs"
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


export default function ProgressPage({ setCurrentPage, setFeedbackData }) {
 const [dateFilter, setDateFilter] = useState('all')
 const [sortBy, setSortBy] = useState('date-desc')
 const [pastPresentations, setPastPresentations] = useState([])
 const [pastSlideDecks, setPastSlideDecks] = useState([])
 const [loading, setLoading] = useState(true)
 const [error, setError] = useState(null)
 const [overallProgressData, setOverallProgressData] = useState([])
 const [skillsData, setSkillsData] = useState([])
 const [activeTab, setActiveTab] = useState('videos')
  // Check if setFeedbackData is available
 const handleViewPresentation = (presentation) => {
   console.log("Viewing presentation:", presentation._id);
  
   // Check if setFeedbackData exists before calling it
   if (typeof setFeedbackData === 'function') {
     setFeedbackData(presentation.feedback_data);
     setCurrentPage("feedback");
   } else {
     console.error("setFeedbackData is not a function. Cannot view presentation details.");
     // Fallback: Navigate to the presentation directly via URL
     window.location.href = `/api/videos/presentations/${presentation._id}`;
   }
 };
  // Fetch user presentations on component mount
 useEffect(() => {
   const fetchPresentations = async () => {
     try {
       setLoading(true)
       const accessToken = localStorage.getItem("accessToken")
      
       if (!accessToken) {
         setError("You must be logged in to view your progress")
         setLoading(false)
         return
       }
      
       // Fetch video presentations
       const apiUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/videos/presentations/`
       console.log("Fetching video presentations from:", apiUrl)
      
       const response = await fetch(apiUrl, {
         headers: {
           "Authorization": `Bearer ${accessToken}`,
           "Content-Type": "application/json"
         }
       })
      
       console.log("API Response status:", response.status);
      
       if (!response.ok) {
         throw new Error(`Failed to fetch presentations: ${response.status}`)
       }
      
       const data = await response.json()
       console.log("Fetched presentations:", data)
      
       // Process video presentations
       if (data && data.length > 0) {
         const processedData = data.map(presentation => ({
           ...presentation,
           type: 'video', // Mark as video presentation
           date: presentation.date || presentation.created_at || new Date().toISOString(),
           score: presentation.score || calculateOverallScore(presentation.feedback_data || {}),
           summary: presentation.summary || generateSummary(presentation.feedback_data || {}),
           title: presentation.title || "Untitled Presentation"
         }))
        
         setPastPresentations(processedData)
         generateProgressData(processedData)
       } else {
         // Set empty data for videos
         setPastPresentations([])
       }
      
       // Now fetch PowerPoint presentations
       const slidesApiUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/presentations/analysis/`
       console.log("Fetching slide presentations from:", slidesApiUrl)
      
       const slidesResponse = await fetch(slidesApiUrl, {
         headers: {
           "Authorization": `Bearer ${accessToken}`,
           "Content-Type": "application/json"
         }
       })
      
       if (!slidesResponse.ok) {
         console.error(`Failed to fetch slide presentations: ${slidesResponse.status}`)
         // Don't throw here, we'll just show empty slides data
       } else {
         const slidesData = await slidesResponse.json()
         console.log("Fetched slide presentations:", slidesData)
        
         if (slidesData && slidesData.length > 0) {
           const processedSlideData = slidesData.map(presentation => ({
             ...presentation,
             type: 'presentation', // Mark as PowerPoint presentation
             date: presentation.date || presentation.created_at || new Date().toISOString(),
             score: presentation.score || calculateSlideScore(presentation.feedback_data || {}),
             summary: presentation.summary || generateSlideSummary(presentation.feedback_data || {}),
             title: presentation.title || "Untitled Slide Deck"
           }))
          
           setPastSlideDecks(processedSlideData)
         } else {
           // Set empty data for slides
           setPastSlideDecks([])
         }
       }
      
       // If both are empty, reset progress data
       if ((data?.length === 0 || !data) && (!slidesData || slidesData?.length === 0)) {
         setOverallProgressData([])
         setSkillsData([])
       }
      
     } catch (err) {
       console.error("Error fetching presentations:", err)
       setError(err.message)
     } finally {
       setLoading(false)
     }
   }
  
   fetchPresentations()
 }, [setCurrentPage])
  // Calculate overall score from feedback data for videos
 const calculateOverallScore = (feedbackData) => {
   if (!feedbackData) return 0
  
   // Example scoring logic - customize based on your feedback structure
   const clarityScore = feedbackData.clarity?.score || 0
   const sentimentScore = feedbackData.sentiment?.score ?
     (feedbackData.sentiment.label === "Positive" ? 90 :
      feedbackData.sentiment.label === "Neutral" ? 70 : 50) : 0
  
   // Calculate average score
   return Math.round((clarityScore + sentimentScore) / 2)
 }
  // Calculate overall score from feedback data for slides
 const calculateSlideScore = (feedbackData) => {
   if (!feedbackData) return 0
  
   // Example scoring logic for slide presentations
   const clarityScore = feedbackData.slide_clarity ? 85 : 0
   const visualScore = feedbackData.visual_quality ? 75 : 0
  
   // Calculate average score
   return Math.round((clarityScore + visualScore) / 2)
 }
  // Generate summary from feedback data for videos
 const generateSummary = (feedbackData) => {
   if (!feedbackData) return "No feedback available"
  
   const points = []
  
   if (feedbackData.speech_rate?.assessment) {
     points.push(feedbackData.speech_rate.assessment)
   }
  
   if (feedbackData.clarity?.score) {
     points.push(`${feedbackData.clarity.score}% clarity`)
   }
  
   if (feedbackData.sentiment?.label) {
     points.push(`${feedbackData.sentiment.label} tone`)
   }
  
   return points.join(', ')
 }
  // Generate summary from feedback data for slides
 const generateSlideSummary = (feedbackData) => {
   if (!feedbackData) return "No feedback available"
  
   const points = []
  
   if (feedbackData.slide_clarity) {
     points.push("Slide content clarity assessment")
   }
  
   if (feedbackData.visual_quality) {
     points.push("Visual design quality feedback")
   }
  
   if (feedbackData.key_topics) {
     points.push("Key topics identified")
   }
  
   if (feedbackData.overall_suggestion) {
     points.push("Improvement suggestions")
   }
  
   return points.length > 0 ? points.join(", ") : "PowerPoint analysis completed"
 }
  // Generate progress data from presentations
 const generateProgressData = (presentations) => {
   // Sort presentations by date
   const sortedPresentations = [...presentations].sort((a, b) =>
     new Date(a.date) - new Date(b.date)
   )
  
   // Create progress data points
   const progressData = sortedPresentations.map(presentation => ({
     date: new Date(presentation.date).toLocaleDateString(),
     score: calculateOverallScore(presentation.feedback_data)
   }))
  
   setOverallProgressData(progressData)
  
   // Generate skills data from the most recent presentation
   const latestPresentation = sortedPresentations[sortedPresentations.length - 1]
   if (latestPresentation && latestPresentation.feedback_data) {
     const skills = [
       { name: "Speaking Pace", score: latestPresentation.feedback_data.speech_rate?.wpm || 0 },
       { name: "Vocal Clarity", score: latestPresentation.feedback_data.clarity?.score || 0 },
       { name: "Grammar", score: latestPresentation.feedback_data.grammar?.score || 0 },
       { name: "Engagement", score: latestPresentation.feedback_data.engagement?.score || 70 },
     ]
    
     setSkillsData(skills)
   }
 }


 // Filter and sort presentations based on active tab
 const filteredItems = activeTab === 'videos'
   ? pastPresentations.filter(filterByDate).sort(sortItems)
   : pastSlideDecks.filter(filterByDate).sort(sortItems);
  
 // Helper functions for filtering and sorting
 function filterByDate(item) {
   if (dateFilter === 'all') return true
   const itemDate = new Date(item.date)
   const today = new Date()
   const daysDiff = (today - itemDate) / (1000 * 60 * 60 * 24)
   return daysDiff <= parseInt(dateFilter)
 }
  function sortItems(a, b) {
   if (sortBy === 'date-desc') return new Date(b.date) - new Date(a.date)
   if (sortBy === 'date-asc') return new Date(a.date) - new Date(b.date)
   if (sortBy === 'score-desc') return b.score - a.score
   if (sortBy === 'score-asc') return a.score - b.score
   return 0
 }


 // Calculate improvement percentage between first and last presentation
 const calculateImprovement = (presentations) => {
   if (presentations.length < 2) return "N/A"
  
   // Sort by date
   const sorted = [...presentations].sort((a, b) =>
     new Date(a.date) - new Date(b.date)
   )
  
   const firstScore = sorted[0].score || 0
   const lastScore = sorted[sorted.length - 1].score || 0
  
   if (firstScore === 0) return "+0%"
  
   const improvement = ((lastScore - firstScore) / firstScore) * 100
   return `${improvement > 0 ? '+' : ''}${Math.round(improvement)}%`
 }


 // Generate key takeaways based on presentation history
 const generateKeyTakeaways = (presentations) => {
   if (presentations.length === 0) return "No presentations yet."
   if (presentations.length === 1) return "Complete more presentations to see trends and insights."
  
   // Sort by date
   const sorted = [...presentations].sort((a, b) =>
     new Date(a.date) - new Date(b.date)
   )
  
   const firstPresentation = sorted[0]
   const lastPresentation = sorted[sorted.length - 1]
  
   // Check for improvement
   const hasImproved = (lastPresentation.score || 0) > (firstPresentation.score || 0)
  
   // Find most common issue
   const issues = presentations.flatMap(p => {
     const feedbackData = p.feedback_data || {}
     const issues = []
    
     if (feedbackData.speech_rate?.assessment === "too fast")
       issues.push("speaking pace")
     if (feedbackData.filler_words?.total > 5)
       issues.push("filler words")
     if (feedbackData.clarity?.score < 70)
       issues.push("clarity")
    
     return issues
   })
  
   const issueCount = {}
   issues.forEach(issue => {
     issueCount[issue] = (issueCount[issue] || 0) + 1
   })
  
   let mostCommonIssue = null
   let maxCount = 0
  
   Object.entries(issueCount).forEach(([issue, count]) => {
     if (count > maxCount) {
       mostCommonIssue = issue
       maxCount = count
     }
   })
  
   // Generate takeaway message
   if (hasImproved) {
     return `Your presentation skills have shown consistent improvement. ${
       mostCommonIssue ? `Focus on improving ${mostCommonIssue} for even better results.` :
       "Keep practicing to maintain your progress."
     }`
   } else {
     return `Your presentations show consistent patterns. ${
       mostCommonIssue ? `Work on improving your ${mostCommonIssue} to see better results.` :
       "Focus on implementing feedback from each session."
     }`
   }
 }


 if (loading) {
   return (
     <div className="flex justify-center items-center h-screen">
       <p className="text-lg font-mono">Loading your progress data...</p>
     </div>
   )
 }


 if (error) {
   return (
     <div className="flex flex-col justify-center items-center h-screen gap-4">
       <p className="text-lg font-mono text-red-500">Error: {error}</p>
       <button
         onClick={() => setCurrentPage("login")}
         className="px-6 py-2 bg-black text-white rounded-full font-mono"
       >
         Go to Login
       </button>
     </div>
   )
 }


 return (
   <div className="max-w-[1280px] mx-auto px-4 py-8">
     <Card className="mb-8">
       <div className="p-6">
         <h2 className="text-2xl font-bold font-mono">Performance Overview</h2>
       </div>
       <CardContent>
         <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
           <div>
             <h3 className="text-lg font-semibold font-mono mb-2">Total Presentations</h3>
             <p className="text-3xl font-bold font-mono">{pastPresentations.length + pastSlideDecks.length}</p>
           </div>
           <div>
             <h3 className="text-lg font-semibold font-mono mb-2">Overall Improvement</h3>
             {pastPresentations.length >= 2 ? (
               <p className="text-3xl font-bold font-mono text-primary">
                 {calculateImprovement(pastPresentations)}
               </p>
             ) : (
               <p className="text-3xl font-bold font-mono">N/A</p>
             )}
           </div>
           <div>
             <h3 className="text-lg font-semibold font-mono mb-2">Best Score</h3>
             {pastPresentations.length > 0 ? (
               <p className="text-3xl font-bold font-mono">
                 {Math.max(...pastPresentations.map(p => p.score || 0))}%
               </p>
             ) : (
               <p className="text-3xl font-bold font-mono">N/A</p>
             )}
           </div>
         </div>
         <div className="mt-6">
           <h3 className="text-lg font-semibold font-mono mb-2">Key Takeaways</h3>
           {pastPresentations.length > 0 ? (
             <p className="font-mono text-[#030303]">
               {generateKeyTakeaways(pastPresentations)}
             </p>
           ) : (
             <p className="font-mono text-[#030303]">
               Upload your first presentation to get personalized feedback and insights.
             </p>
           )}
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
             {filteredItems.length > 0 ? (
               filteredItems.map((item, index) => (
                 <TableRow key={index}>
                   <TableCell className="font-mono">
                     {new Date(item.date).toLocaleDateString()}
                   </TableCell>
                   <TableCell className="font-mono">
                     {item.title}
                     <span className="ml-2 px-2 py-1 bg-gray-100 rounded text-xs">
                       {item.type === 'video' ? 'Video' : 'PowerPoint'}
                     </span>
                   </TableCell>
                   <TableCell className="font-mono">
                     {item.score}
                   </TableCell>
                   <TableCell className="font-mono">
                     {item.summary}
                   </TableCell>
                   <TableCell>
                     <Button
                       variant="outline"
                       size="sm"
                       onClick={() => handleViewPresentation(item)}
                       className="flex items-center gap-1"
                     >
                       <Eye className="h-4 w-4" />
                       View
                     </Button>
                   </TableCell>
                 </TableRow>
               ))
             ) : (
               <TableRow>
                 <TableCell colSpan={5} className="text-center py-8 text-gray-500 font-mono">
                   {loading ? "Loading presentations..." :
                     activeTab === 'videos'
                       ? "No video presentations found. Upload a video to get started!"
                       : "No PowerPoint presentations found. Upload a slide deck to get started!"}
                 </TableCell>
               </TableRow>
             )}
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

