import { useState } from 'react'
import { format, setHours } from 'date-fns'

const PresentationForm = ({ isOpen, onClose, onSubmit, editingPresentation = null }) => {
  const [formData, setFormData] = useState(editingPresentation || {
    title: '',
    date: format(new Date(), 'yyyy-MM-dd'),
    startTime: '09:00',
    endTime: '10:00',
    color: '#4F46E5' // Default primary color
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md">
        <h2 className="text-2xl font-bold font-mono text-[#030303] mb-6">
          {editingPresentation ? 'Edit Presentation' : 'Add Presentation'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-mono text-sm mb-1">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full p-2 border rounded-lg font-mono"
              required
            />
          </div>

          <div>
            <label className="block font-mono text-sm mb-1">Date</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({...formData, date: e.target.value})}
              className="w-full p-2 border rounded-lg font-mono"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block font-mono text-sm mb-1">Start Time</label>
              <select
                value={formData.startTime}
                onChange={(e) => setFormData({...formData, startTime: e.target.value})}
                className="w-full p-2 border rounded-lg font-mono"
                required
              >
                {Array.from({ length: 24 }).map((_, i) => (
                  <option key={i} value={`${i.toString().padStart(2, '0')}:00`}>
                    {format(setHours(new Date(), i), 'h:00 a')}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-mono text-sm mb-1">End Time</label>
              <select
                value={formData.endTime}
                onChange={(e) => setFormData({...formData, endTime: e.target.value})}
                className="w-full p-2 border rounded-lg font-mono"
                required
              >
                {Array.from({ length: 24 }).map((_, i) => (
                  <option key={i} value={`${i.toString().padStart(2, '0')}:00`}>
                    {format(setHours(new Date(), i), 'h:00 a')}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block font-mono text-sm mb-1">Color</label>
            <input
              type="color"
              value={formData.color}
              onChange={(e) => setFormData({...formData, color: e.target.value})}
              className="w-full h-10 p-1 rounded-lg"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 font-mono font-semibold hover:text-primary transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-black text-white rounded-lg font-mono font-semibold hover:bg-primary transition-colors"
            >
              {editingPresentation ? 'Update' : 'Add'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default PresentationForm 