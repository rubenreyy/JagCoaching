import { useState } from 'react'
import Navbar from './components/layout/Navbar'
import Dashboard from './components/dashboard/Dashboard'

function App() {
  return (
    <div className="min-h-screen bg-[#EEEEEE]">
      <Navbar />
      <Dashboard />
    </div>
  )
}

export default App
