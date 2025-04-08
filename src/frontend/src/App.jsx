import LiveAnalysis from './components/live/LiveAnalysis';
import { useState } from 'react'
import Navbar from './components/layout/Navbar'
import Dashboard from './components/dashboard/Dashboard'
import Upload from './components/upload/Upload'
import Schedule from './components/schedule/Schedule'
import Feedback from './components/feedback/Feedback'
import ProgressPage from './components/progress/ProgressPage'
import Login from './components/auth/Login'
import Signup from './components/auth/Signup'
import AccountPage from './components/account/AccountPage'
import { LiveSessionProvider } from './contexts/LiveSessionContext'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [accessToken, setAccessToken] = useState(null)
  const [feedbackData, setFeedbackData] = useState(null)

  const mockFeedback = {
    eyeContact: 82,
    facialExpressions: ['happy', 'engaged', 'neutral'],
    posture: 'upright'
  };  

  return (
    <LiveSessionProvider>
      <div className="min-h-screen bg-[#EEEEEE]">
        <Navbar 
          currentPage={currentPage} 
          setCurrentPage={setCurrentPage}
          isLoggedIn={isLoggedIn}
          setIsLoggedIn={setIsLoggedIn}
          accessToken={accessToken}
          setAccessToken={setAccessToken}
        />
        {currentPage === 'dashboard' && <Dashboard setCurrentPage={setCurrentPage} />}
        {currentPage === 'upload' && (
          <Upload 
            setCurrentPage={setCurrentPage} 
            setFeedbackData={setFeedbackData} 
          />
        )}
        {currentPage === 'schedule' && <Schedule />}
        {currentPage === 'feedback' && <Feedback feedbackData={feedbackData} />}
        {currentPage === 'progress' && <ProgressPage setCurrentPage={setCurrentPage} />}
        {currentPage === 'login' && <Login setCurrentPage={setCurrentPage} setIsLoggedIn={setIsLoggedIn} />}
        {currentPage === 'signup' && <Signup setCurrentPage={setCurrentPage} setIsLoggedIn={setIsLoggedIn} />}
        {currentPage === 'account' && <AccountPage setCurrentPage={setCurrentPage} setIsLoggedIn={setIsLoggedIn} />}
        {currentPage === 'live' && <LiveAnalysis />}
      </div>
    </LiveSessionProvider>
  )
}

export default App
