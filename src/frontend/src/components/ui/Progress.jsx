const Progress = ({ value, className = '' }) => {
  return (
    <div className={`h-2 bg-gray-200 rounded-full overflow-hidden ${className}`}>
      <div 
        className="h-full bg-primary transition-all duration-300 ease-in-out"
        style={{ width: `${value}%` }}
      />
    </div>
  )
}

export { Progress } 