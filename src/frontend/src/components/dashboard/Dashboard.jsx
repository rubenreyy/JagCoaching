const Dashboard = () => {
  return (
    <div className="max-w-[1280px] mx-auto py-20 flex flex-col gap-7">
      {/* Upload Section */}
      <section className="w-full bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-[#1E1E1E] text-3xl font-bold font-mono mb-4">
          Upload Presentation
        </h2>
        <button className="w-full bg-[#030303] text-white rounded-2xl py-4 font-mono font-semibold text-3xl hover:bg-primary transition-colors flex items-center justify-center gap-3">
          <img 
            src="../src/assets/AiOutlineToTop.png" 
            alt="Upload" 
            className="w-6 h-6" 
          />
          Upload Video/Slides
        </button>
        <p className="mt-4 text-black text-xl font-mono">
          Upload your presentation video and slides for AI analysis
        </p>
      </section>

      {/* Recent Feedback Section */}
      <section className="w-full bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-[#1E1E1E] text-3xl font-bold font-mono mb-6">
          Recent Feedback
        </h2>
        <div className="space-y-6">
          <div className="space-y-2">
            <p className="text-black text-xl font-mono">Speech Clarity: 85%</p>
            <div className="w-full h-4 bg-[#EEEEEE] rounded-full">
              <div className="w-[85%] h-full bg-[#030303] rounded-full" />
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-black text-xl font-mono">Eye Contact: 70%</p>
            <div className="w-full h-4 bg-[#EEEEEE] rounded-full">
              <div className="w-[70%] h-full bg-[#030303] rounded-full" />
            </div>
          </div>
          <div className="space-y-2">
            <p className="text-black text-xl font-mono">Content Organization: 90%</p>
            <div className="w-full h-4 bg-[#EEEEEE] rounded-full">
              <div className="w-[90%] h-full bg-[#030303] rounded-full" />
            </div>
          </div>
        </div>
        <button className="mt-6 w-full border-2 border-[#EEEEEE] text-[#030303] rounded-2xl py-3 font-mono font-semibold hover:bg-primary hover:text-white hover:border-primary transition-colors">
          View Full Feedback
        </button>
      </section>

      {/* Quick Tips Section */}
      <section className="w-full bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-[#1E1E1E] text-3xl font-bold font-mono mb-4">
          Quick Tips
        </h2>
        <ul className="space-y-2 text-black text-xl font-mono">
          <li>• Practice your presentation in front of a mirror</li>
          <li>• Use Pauses effectively to emphasize key points</li>
          <li>• Maintain eye contact with your audience</li>
          <li>• Keep your slides simple and visually appealing</li>
          <li>• Take a deep breath. You got this!</li>
        </ul>
      </section>

      {/* Upcoming Presentations Section */}
      <section className="w-full bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-[#1E1E1E] text-3xl font-bold font-mono mb-4">
          Upcoming Presentations
        </h2>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <img 
              src="../src/assets/AiFillCalendar.png" 
              alt="Calendar" 
              className="w-6 h-6 text-primary" 
            />
            <p className="text-black text-xl font-mono">Project Pitch - March 1, 2025</p>
          </div>
          <div className="flex items-center gap-3">
            <img 
              src="../src/assets/AiFillCalendar.png" 
              alt="Calendar" 
              className="w-6 h-6 text-primary" 
            />
            <p className="text-black text-xl font-mono">Research Symposium - April 15, 2025</p>
          </div>
        </div>
        <button className="mt-6 w-full border-2 border-[#EEEEEE] text-[#030303] rounded-2xl py-3 font-mono font-semibold hover:bg-primary hover:text-white hover:border-primary transition-colors">
          Add Presentation
        </button>
      </section>

      {/* Progress Tracking Section */}
      <section className="w-full bg-white rounded-2xl shadow-md p-6">
        <h2 className="text-[#1E1E1E] text-3xl font-bold font-mono mb-4">
          Progress Tracking
        </h2>
        <div className="flex justify-center mb-6">
          <img 
            src="../src/assets/AiFillFund.png" 
            alt="Progress" 
            className="w-48 h-48 text-primary" 
          />
        </div>
        <button className="w-full border-2 border-[#EEEEEE] text-[#030303] rounded-2xl py-3 font-mono font-semibold hover:bg-primary hover:text-white hover:border-primary transition-colors">
          View Detailed Progress
        </button>
      </section>
    </div>
  )
}

export default Dashboard