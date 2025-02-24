import React, { useState } from 'react'

const Select = ({ value, onChange, children, className = "", ...props }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className={`relative ${className}`} {...props}>
      {React.Children.map(children, child => {
        if (child.type === SelectTrigger) {
          return React.cloneElement(child, { 
            value, 
            onClick: () => setIsOpen(!isOpen),
            isOpen 
          })
        }
        if (child.type === SelectContent) {
          return isOpen && React.cloneElement(child, { 
            value, 
            onChange: (newValue) => {
              onChange(newValue)
              setIsOpen(false)
            }
          })
        }
        return child
      })}
    </div>
  )
}

const SelectTrigger = ({ value, onClick, isOpen, children, className = "", ...props }) => {
  return (
    <button 
      onClick={onClick}
      className={`flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    >
      {children}
      <span className={`ml-2 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>▼</span>
    </button>
  )
}

const SelectContent = ({ children, value, onChange, className = "" }) => {
  return (
    <div 
      className={`absolute z-50 w-full mt-1 overflow-hidden rounded-md border bg-white text-black shadow-md animate-in fade-in-80 ${className}`}
    >
      <div className="p-1">
        {React.Children.map(children, child => 
          React.cloneElement(child, { 
            onClick: () => onChange(child.props.value),
            active: child.props.value === value
          })
        )}
      </div>
    </div>
  )
}

const SelectItem = ({ value, children, onClick, active, className = "" }) => {
  return (
    <button
      onClick={onClick}
      className={`relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 px-2 text-sm outline-none hover:bg-gray-100 ${active ? 'bg-gray-100' : ''} ${className}`}
    >
      {children}
    </button>
  )
}

const SelectValue = ({ children, placeholder = "", className = "" }) => {
  return (
    <span className={`block truncate ${className}`}>
      {children || placeholder}
    </span>
  )
}

export { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } 