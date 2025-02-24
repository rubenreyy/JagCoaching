import { useState } from 'react'
import Calendar from './Calendar'
import UpcomingPresentations from './UpcomingPresentations'
import PresentationForm from './PresentationForm'

const Schedule = () => {
  const [view, setView] = useState('month')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [presentations, setPresentations] = useState([
    {
      id: 1,
      title: 'Midterm Presentation',
      date: '2024-03-15',
      startTime: '10:00',
      endTime: '11:00',
      color: '#4F46E5'
    },
    {
      id: 2,
      title: 'Group Project Demo',
      date: '2024-04-02',
      startTime: '14:00',
      endTime: '15:00',
      color: '#059669'
    }
  ])
  const [editingPresentation, setEditingPresentation] = useState(null)

  const handleAddPresentation = (newPresentation) => {
    setPresentations([
      ...presentations,
      {
        ...newPresentation,
        id: Date.now()
      }
    ])
  }

  const handleEditPresentation = (presentation) => {
    setPresentations(presentations.map(p => 
      p.id === presentation.id ? presentation : p
    ))
  }

  const handleDeletePresentation = (id) => {
    setPresentations(presentations.filter(p => p.id !== id))
  }

  return (
    <div className="max-w-[1280px] mx-auto px-4 py-8">
      {/* View Toggle and Add Button */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex gap-4">
          {['month', 'week', 'day'].map((viewType) => (
            <button
              key={viewType}
              onClick={() => setView(viewType)}
              className={`px-4 py-2 font-mono font-semibold text-lg capitalize
                ${view === viewType 
                  ? 'text-primary border-b-2 border-primary' 
                  : 'text-[#030303] hover:text-primary transition-colors'
                }`}
            >
              {viewType}
            </button>
          ))}
        </div>
        <button 
          onClick={() => {
            setEditingPresentation(null)
            setIsFormOpen(true)
          }}
          className="bg-black text-white px-6 py-2 rounded-full font-mono font-semibold hover:bg-primary transition-colors"
        >
          + Add Presentation
        </button>
      </div>

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left Column - Calendar */}
        <div className="w-full lg:w-3/4">
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-2xl font-bold font-mono text-[#030303] mb-6">
              Calendar
            </h2>
            <Calendar 
              view={view} 
              setView={setView} 
              presentations={presentations}
            />
          </div>
        </div>

        {/* Right Column - Upcoming Presentations */}
        <div className="w-full lg:w-1/4">
          <UpcomingPresentations 
            presentations={presentations}
            onEdit={(presentation) => {
              setEditingPresentation(presentation)
              setIsFormOpen(true)
            }}
            onDelete={handleDeletePresentation}
          />
        </div>
      </div>

      <PresentationForm 
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={editingPresentation ? handleEditPresentation : handleAddPresentation}
        editingPresentation={editingPresentation}
      />
    </div>
  )
}

export default Schedule 