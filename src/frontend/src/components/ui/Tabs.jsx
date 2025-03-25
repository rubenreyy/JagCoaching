import React, { useState } from 'react'

const Tabs = ({ defaultValue, children, className = '' }) => {
  const [activeTab, setActiveTab] = useState(defaultValue)
  
  const childrenWithProps = React.Children.map(children, child => {
    if (child.type === TabsContent) {
      return React.cloneElement(child, { active: child.props.value === activeTab })
    }
    if (child.type === TabsList) {
      return React.cloneElement(child, { activeTab, setActiveTab })
    }
    return child
  })

  return <div className={className}>{childrenWithProps}</div>
}

const TabsList = ({ children, activeTab, setActiveTab }) => {
  return (
    <div className="flex gap-4 mb-6">
      {React.Children.map(children, child =>
        React.cloneElement(child, { 
          active: child.props.value === activeTab, 
          onClick: () => setActiveTab(child.props.value) 
        })
      )}
    </div>
  )
}

const TabsTrigger = ({ value, children, active, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 font-mono font-semibold text-lg capitalize
        ${active 
          ? 'text-primary border-b-2 border-primary' 
          : 'text-[#030303] hover:text-primary transition-colors'
        }`}
    >
      {children}
    </button>
  )
}

const TabsContent = ({ value, children, active }) => {
  if (!active) return null
  return <div>{children}</div>
}

export { Tabs, TabsList, TabsTrigger, TabsContent } 