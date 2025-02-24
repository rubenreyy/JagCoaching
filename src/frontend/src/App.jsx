import { useState } from 'react'
import Navbar from './components/layout/Navbar'
import Dashboard from './components/dashboard/Dashboard'
import Upload from './components/upload/Upload'
import Schedule from './components/schedule/Schedule'
import Feedback from './components/feedback/Feedback'
import ProgressPage from './components/progress/ProgressPage'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  return (
    <div className="min-h-screen bg-[#EEEEEE]">
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      {currentPage === 'dashboard' && <Dashboard setCurrentPage={setCurrentPage} />}
      {currentPage === 'upload' && <Upload setCurrentPage={setCurrentPage}/>}
      {currentPage === 'schedule' && <Schedule />}
      {currentPage === 'feedback' && <Feedback />}
      {currentPage === 'progress' && <ProgressPage setCurrentPage={setCurrentPage} />}
    </div>
  )
}

export default App
