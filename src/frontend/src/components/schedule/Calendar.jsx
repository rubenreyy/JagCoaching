import { useState } from 'react'
import { 
  format, 
  addMonths, 
  subMonths,
  addWeeks,
  subWeeks,
  addDays,
  subDays, 
  startOfMonth, 
  endOfMonth, 
  eachDayOfInterval,
  isSameMonth,
  startOfWeek,
  endOfWeek,
  isSameDay,
  parseISO,
  setHours,
  getHours,
} from 'date-fns'

const Calendar = ({ view, setView, presentations }) => {
  const [currentDate, setCurrentDate] = useState(new Date())

  const handleNavigationClick = (direction) => {
    switch (view) {
      case 'month':
        setCurrentDate(direction === 'prev' ? subMonths(currentDate, 1) : addMonths(currentDate, 1))
        break
      case 'week':
        setCurrentDate(direction === 'prev' ? subWeeks(currentDate, 1) : addWeeks(currentDate, 1))
        break
      case 'day':
        setCurrentDate(direction === 'prev' ? subDays(currentDate, 1) : addDays(currentDate, 1))
        break
    }
  }

  const handleDateClick = (date) => {
    setCurrentDate(date)
    setView('day')
  }

  const isNightTime = (hour) => {
    return hour < 6 || hour >= 18
  }

  const renderMonthView = () => {
    const start = startOfMonth(currentDate)
    const end = endOfMonth(currentDate)
    const days = eachDayOfInterval({ start, end })

    return (
      <div className="grid grid-cols-7 gap-1">
        {/* Week day headers */}
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="p-2 text-center font-mono font-semibold">
            {day}
          </div>
        ))}
        
        {/* Calendar days */}
        {days.map(day => (
          <div
            key={day.toString()}
            className={`p-2 border rounded-lg hover:bg-gray-50 cursor-pointer
              ${!isSameMonth(day, currentDate) ? 'text-gray-400' : ''}
              ${isSameDay(day, new Date()) ? 'bg-primary text-white hover:bg-primary/90' : ''}`}
          >
            <button
              onClick={() => handleDateClick(day)}
              className="w-full text-center mb-1"
            >
              {format(day, 'd')}
            </button>
            {/* Presentations for this day */}
            <div className="space-y-1">
              {presentations
                .filter(pres => isSameDay(parseISO(pres.date), day))
                .map((pres, idx) => (
                  <div 
                    key={idx}
                    className="text-xs p-1 rounded truncate"
                    style={{
                      backgroundColor: `${pres.color}20`,
                      borderLeft: `2px solid ${pres.color}`,
                      color: pres.color
                    }}
                  >
                    {pres.title}
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderWeekView = () => {
    const start = startOfWeek(currentDate)
    const end = endOfWeek(currentDate)
    const days = eachDayOfInterval({ start, end })

    return (
      <div className="grid grid-cols-7 gap-1 h-[600px]">
        {days.map(day => (
          <div key={day.toString()} className="flex flex-col h-full">
            <button
              onClick={() => handleDateClick(day)}
              className="flex flex-col hover:bg-gray-50"
            >
              <div className="p-2 text-center font-mono font-semibold sticky top-0 bg-white z-10">
                {format(day, 'EEE')}
              </div>
              <div className={`p-2 text-center font-mono border-b-2 sticky top-10 bg-white z-10
                ${isSameDay(day, new Date()) ? 'text-primary border-primary' : 'border-transparent'}`}>
                {format(day, 'd')}
              </div>
            </button>
            {/* Presentations for this day */}
            <div className="flex-1 border-r overflow-y-auto">
              {presentations
                .filter(pres => isSameDay(parseISO(pres.date), day))
                .map((pres, idx) => (
                  <div 
                    key={idx}
                    className="p-2 text-sm border-b cursor-pointer"
                    style={{
                      backgroundColor: `${pres.color}20`,
                      borderLeft: `4px solid ${pres.color}`
                    }}
                  >
                    <div className="font-semibold">{pres.startTime}</div>
                    <div>{pres.title}</div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderDayView = () => {
    return (
      <div className="h-[600px] overflow-y-auto">
        <div className="sticky top-0 bg-white p-2 text-center font-mono font-semibold border-b z-10">
          {format(currentDate, 'EEEE, MMMM d, yyyy')}
        </div>
        <div className="divide-y">
          {Array.from({ length: 24 }).map((_, hour) => {
            const isNight = isNightTime(hour)
            return (
              <div 
                key={hour}
                className={`flex items-center group
                  ${isNight ? 'bg-gray-50' : ''}`}
              >
                <div className="w-32 p-4 text-right font-mono text-gray-500 sticky left-0">
                  {format(setHours(currentDate, hour), 'h:00 a')}
                </div>
                <div className="flex-1 p-4 min-h-[80px] border-l">
                  {presentations
                    .filter(pres => 
                      isSameDay(parseISO(pres.date), currentDate) && 
                      parseInt(pres.startTime) === hour
                    )
                    .map((pres, idx) => (
                      <div 
                        key={idx}
                        className="p-2 rounded cursor-pointer"
                        style={{
                          backgroundColor: `${pres.color}20`,
                          borderLeft: `4px solid ${pres.color}`
                        }}
                      >
                        {pres.title}
                      </div>
                    ))}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Calendar navigation */}
      <div className="flex justify-between items-center mb-4">
        <button
          onClick={() => handleNavigationClick('prev')}
          className="p-2 hover:text-primary transition-colors"
        >
          Previous
        </button>
        <h3 className="font-mono font-semibold">
          {view === 'day' 
            ? format(currentDate, 'MMMM d, yyyy')
            : format(currentDate, 'MMMM yyyy')}
        </h3>
        <button
          onClick={() => handleNavigationClick('next')}
          className="p-2 hover:text-primary transition-colors"
        >
          Next
        </button>
      </div>

      {/* Calendar view */}
      {view === 'month' && renderMonthView()}
      {view === 'week' && renderWeekView()}
      {view === 'day' && renderDayView()}
    </div>
  )
}

export default Calendar 