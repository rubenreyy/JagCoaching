import { useState } from 'react'
import { Menu, X } from 'lucide-react'

const Navbar = ({ currentPage, setCurrentPage }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <nav className="w-full h-[79px] bg-[#030303] px-4 relative">
      <div className="max-w-[1280px] h-full mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-8">
          <button 
            onClick={() => setCurrentPage('dashboard')}
            className="text-white text-3xl font-bold font-mono hover:text-primary transition-colors"
          >
            JagCoach
          </button>
          
          {/* Navigation Links - Desktop */}
          <div className="hidden md:flex gap-8">
            <button 
              onClick={() => setCurrentPage('upload')}
              className={`text-white text-xl font-mono font-light hover:text-primary transition-colors
                ${currentPage === 'upload' ? 'text-primary' : ''}`}
            >
              Upload
            </button>
            <button 
              onClick={() => setCurrentPage('feedback')}
              className={`text-white text-xl font-mono font-light hover:text-primary transition-colors
                ${currentPage === 'feedback' ? 'text-primary' : ''}`}
            >
              Feedback
            </button>
            <button 
              onClick={() => setCurrentPage('schedule')}
              className={`text-white text-xl font-mono font-light hover:text-primary transition-colors
                ${currentPage === 'schedule' ? 'text-primary' : ''}`}
            >
              Schedule
            </button>
          </div>
        </div>

        {/* Auth Buttons - Desktop */}
        <div className="hidden md:flex gap-3">
          <button className="bg-white rounded-[22.5px] px-8 py-2 font-mono font-semibold text-base text-[#030303] hover:bg-primary hover:text-white transition-colors">
            Login
          </button>
          <button className="bg-white rounded-[22.5px] px-8 py-2 font-mono font-semibold text-base text-[#030303] hover:bg-primary hover:text-white transition-colors">
            Sign Up
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="md:hidden text-white"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="absolute top-[79px] left-0 w-full bg-[#030303] py-4 px-4 md:hidden">
          <div className="flex flex-col gap-4">
            <button 
              onClick={() => {
                setCurrentPage('dashboard')
                setIsMenuOpen(false)
              }}
              className={`text-white text-xl font-mono font-light hover:text-primary transition-colors
                ${currentPage === 'dashboard' ? 'text-primary' : ''}`}
            >
              Upload
            </button>
            <button 
              onClick={() => {
                setCurrentPage('feedback')
                setIsMenuOpen(false)
              }}
              className={`text-white text-xl font-mono font-light hover:text-primary transition-colors
                ${currentPage === 'feedback' ? 'text-primary' : ''}`}
            >
              Feedback
            </button>
            <button 
              onClick={() => {
                setCurrentPage('schedule')
                setIsMenuOpen(false)
              }}
              className={`text-white text-xl font-mono font-light hover:text-primary transition-colors
                ${currentPage === 'schedule' ? 'text-primary' : ''}`}
            >
              Schedule
            </button>
            <div className="flex flex-col gap-3 pt-4">
              <button className="bg-white rounded-[22.5px] py-2 font-mono font-semibold text-base text-[#030303] hover:bg-primary hover:text-white transition-colors">
                Login
              </button>
              <button className="bg-white rounded-[22.5px] py-2 font-mono font-semibold text-base text-[#030303] hover:bg-primary hover:text-white transition-colors">
                Sign Up
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}

export default Navbar
