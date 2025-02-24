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

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  return (
    <div className="min-h-screen bg-[#EEEEEE]">
      <Navbar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage}
        isLoggedIn={isLoggedIn}
        setIsLoggedIn={setIsLoggedIn}
      />
      {currentPage === 'dashboard' && <Dashboard setCurrentPage={setCurrentPage} />}
      {currentPage === 'upload' && <Upload setCurrentPage={setCurrentPage} />}
      {currentPage === 'schedule' && <Schedule />}
      {currentPage === 'feedback' && <Feedback />}
      {currentPage === 'progress' && <ProgressPage setCurrentPage={setCurrentPage} />}
      {currentPage === 'login' && <Login setCurrentPage={setCurrentPage} setIsLoggedIn={setIsLoggedIn} />}
      {currentPage === 'signup' && <Signup setCurrentPage={setCurrentPage} setIsLoggedIn={setIsLoggedIn} />}
      {currentPage === 'account' && <AccountPage setCurrentPage={setCurrentPage} setIsLoggedIn={setIsLoggedIn} />}
    </div>
  )
}

export default App
