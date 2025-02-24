import { useState } from 'react'
import { Menu, X } from 'lucide-react'

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <nav className="w-full h-[79px] bg-[#030303] px-4 relative">
      <div className="max-w-[1280px] h-full mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-8">
          <h1 className="text-white text-3xl font-bold font-mono">
            JagCoach
          </h1>
          
          {/* Navigation Links - Desktop */}
          <div className="hidden md:flex gap-8">
            <a 
              href="/upload" 
              className="text-white text-xl font-mono font-light hover:text-primary transition-colors"
            >
              Upload
            </a>
            <a 
              href="/feedback" 
              className="text-white text-xl font-mono font-light hover:text-primary transition-colors"
            >
              Feedback
            </a>
            <a 
              href="/schedule" 
              className="text-white text-xl font-mono font-light hover:text-primary transition-colors"
            >
              Schedule
            </a>
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
            <a 
              href="/upload" 
              className="text-white text-xl font-mono font-light hover:text-primary transition-colors"
            >
              Upload
            </a>
            <a 
              href="/feedback" 
              className="text-white text-xl font-mono font-light hover:text-primary transition-colors"
            >
              Feedback
            </a>
            <a 
              href="/schedule" 
              className="text-white text-xl font-mono font-light hover:text-primary transition-colors"
            >
              Schedule
            </a>
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
