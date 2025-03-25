import { format, parseISO } from 'date-fns'

const UpcomingPresentations = ({ presentations, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-2xl shadow-md p-6">
      <h2 className="text-xl font-semibold font-mono text-[#030303] mb-6">
        Upcoming Presentations
      </h2>
      <div className="space-y-6">
        {presentations
          .sort((a, b) => new Date(a.date) - new Date(b.date))
          .map((presentation) => (
          <div key={presentation.id} className="flex justify-between items-start">
            <div>
              <h3 className="font-mono text-[#030303]">{presentation.title}</h3>
              <p className="font-mono text-[#8E8E8E] text-sm">
                {format(parseISO(presentation.date), 'MMMM d, yyyy')}
              </p>
              <p className="font-mono text-[#8E8E8E] text-sm">
                {presentation.startTime} - {presentation.endTime}
              </p>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={() => onEdit(presentation)}
                className="p-2 hover:text-primary transition-colors"
              >
                <img 
                  src="../src/assets/AiFillEdit.png" 
                  alt="Edit" 
                  className="w-5 h-5" 
                />
              </button>
              <button 
                onClick={() => onDelete(presentation.id)}
                className="p-2 hover:text-primary transition-colors"
              >
                <img 
                  src="../src/assets/Vector.png" 
                  alt="Delete" 
                  className="w-5 h-5" 
                />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default UpcomingPresentations 