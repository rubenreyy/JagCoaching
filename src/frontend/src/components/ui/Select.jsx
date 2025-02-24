import React, { useState } from 'react'

const Select = ({ value, onChange, children, className = "", ...props }) => {
  return (
    <div className={`relative ${className}`} {...props}>
      {React.Children.map(children, child => {
        if (child.type === SelectTrigger || child.type === SelectContent) {
          return React.cloneElement(child, { value, onChange })
        }
        return child
      })}
    </div>
  )
}

const SelectTrigger = ({ value, onChange, children, className = "", ...props }) => {
  const [isOpen, setIsOpen] = useState(false)
  
  return (
    <>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={`flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
        {...props}
      >
        {children}
        <span className="ml-2">▼</span>
      </button>
      {isOpen && (
        <SelectContent value={value} onChange={onChange} setIsOpen={setIsOpen}>
          {React.Children.toArray(children).find(child => child.type === SelectContent)?.props.children}
        </SelectContent>
      )}
    </>
  )
}

const SelectContent = ({ children, value, onChange, setIsOpen, className = "" }) => {
  return (
    <div 
      className={`absolute z-50 w-full mt-1 overflow-hidden rounded-md border bg-white text-black shadow-md animate-in fade-in-80 ${className}`}
    >
      <div className="p-1">
        {React.Children.map(children, child => 
          React.cloneElement(child, { 
            onClick: () => {
              onChange(child.props.value)
              setIsOpen(false)
            },
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