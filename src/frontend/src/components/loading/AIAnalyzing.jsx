import { useState, useEffect } from "react"
import { motion } from "framer-motion"

const loadingMessages = [
  "Transcribing your presentation...",
  "Analyzing speech patterns...",
  "Evaluating speaking pace...",
  "Detecting filler words...",
  "Measuring clarity...",
  "Analyzing sentiment...",
  "Identifying key topics...",
  "Generating feedback..."
]

const AIAnalyzing = ({ onComplete, analysisData }) => {
  const [messageIndex, setMessageIndex] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    console.log("AIAnalyzing: Starting analysis animation")
    
    const messageInterval = setInterval(() => {
      setMessageIndex((prevIndex) => {
        console.log("Updating loading message")
        return (prevIndex + 1) % loadingMessages.length
      })
    }, 3000)

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + 1
        if (newProgress >= 100) {
          console.log("Analysis animation complete")
          clearInterval(progressInterval)
          clearInterval(messageInterval)
          if (analysisData) {
            console.log("Analysis data received:", analysisData)
            onComplete(analysisData)
          }
          return 100
        }
        return newProgress
      })
    }, 300)

    return () => {
      console.log("Cleaning up analysis intervals")
      clearInterval(messageInterval)
      clearInterval(progressInterval)
    }
  }, [onComplete, analysisData])

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#EEEEEE] z-50">
      <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-lg">
        <div className="flex items-center justify-center gap-3 mb-8">
          <h2 className="text-2xl font-bold font-mono">AI JagCoach Analyzing</h2>
          {/* Particle Container - Next to text */}
          <div className="relative w-24 h-8">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-primary rounded-full opacity-70"
                initial={{
                  x: 0,
                  y: "50%",
                  scale: 0,
                }}
                animate={{
                  x: [0, 80],
                  scale: [0, 1, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Number.POSITIVE_INFINITY,
                  delay: i * 0.3,
                  ease: "linear",
                }}
              />
            ))}
          </div>
        </div>

        <div className="relative w-full h-72 mb-8">
          {/* AI Coach */}
          <motion.svg
            viewBox="0 0 100 100"
            className="absolute top-0 left-0 w-1/2 h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <circle cx="50" cy="30" r="20" fill="#030303" />
            <rect x="35" y="55" width="30" height="40" fill="#030303" />
            <circle cx="43" cy="25" r="3" fill="white" />
            <circle cx="57" cy="25" r="3" fill="white" />
            <path d="M45 35 Q50 40 55 35" stroke="white" strokeWidth="2" fill="none" />
          </motion.svg>

          {/* Student */}
          <motion.svg
            viewBox="0 0 100 100"
            className="absolute top-0 right-0 w-1/2 h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
          >
            <circle cx="50" cy="30" r="20" fill="#0500FF" />
            <rect x="35" y="55" width="30" height="40" fill="#0500FF" />
            <circle cx="43" cy="25" r="3" fill="white" />
            <circle cx="57" cy="25" r="3" fill="white" />
            <path d="M45 35 Q50 40 55 35" stroke="white" strokeWidth="2" fill="none" />
          </motion.svg>

          {/* Analysis Waves - Updated blue wave direction */}
          <motion.svg
            viewBox="0 0 100 100"
            className="absolute top-0 left-0 w-full h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
          >
            {/* Black wave - left to right */}
            <motion.path
              d="M10 50 Q25 40, 40 50 T70 50 T100 50"
              stroke="#030303"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }}
            />
            {/* Blue wave - right to left */}
            <motion.path
              d="M100 60 Q85 70, 70 60 T40 60 T10 60"
              stroke="#0500FF"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, delay: 0.5 }}
            />
          </motion.svg>
        </div>

        <motion.div
          className="text-center text-lg font-mono font-medium text-[#030303] mb-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          key={messageIndex}
        >
          {loadingMessages[messageIndex]}
        </motion.div>

        <div className="w-full bg-[#EEEEEE] rounded-full h-2.5">
          <div 
            className="bg-primary h-2.5 rounded-full transition-all duration-150"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  )
}

export default AIAnalyzing 