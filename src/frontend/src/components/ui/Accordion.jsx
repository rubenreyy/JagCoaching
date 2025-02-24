import React, { useState } from 'react'
import { ChevronDown } from 'lucide-react'

const Accordion = ({ children, type = 'single', collapsible = true }) => {
  const [openItems, setOpenItems] = useState(new Set())

  const toggleItem = (value) => {
    setOpenItems(prev => {
      const newOpenItems = new Set(prev)
      if (newOpenItems.has(value)) {
        newOpenItems.delete(value)
      } else {
        if (type === 'single') {
          newOpenItems.clear()
        }
        newOpenItems.add(value)
      }
      return newOpenItems
    })
  }

  return (
    <div className="bg-white">
      {React.Children.map(children, child =>
        React.cloneElement(child, {
          isOpen: openItems.has(child.props.value),
          onToggle: () => toggleItem(child.props.value)
        })
      )}
    </div>
  )
}

const AccordionItem = ({ children, value, isOpen, onToggle }) => {
  return (
    <div>
      {React.Children.map(children, child => {
        if (child.type === AccordionTrigger) {
          return React.cloneElement(child, { isOpen, onToggle })
        }
        if (child.type === AccordionContent) {
          return React.cloneElement(child, { isOpen })
        }
        return child
      })}
    </div>
  )
}

const AccordionTrigger = ({ children, isOpen, onToggle }) => {
  return (
    <button
      className="flex w-full items-center justify-between px-6 py-4 text-lg font-mono font-semibold text-[#030303] hover:text-primary transition-colors"
      onClick={onToggle}
    >
      {children}
      <ChevronDown
        className={`h-5 w-5 transition-transform duration-200 ${
          isOpen ? 'rotate-180' : ''
        }`}
      />
    </button>
  )
}

const AccordionContent = ({ children, isOpen }) => {
  return (
    <div 
      className={`overflow-hidden transition-all duration-200 ease-in-out
        ${isOpen ? 'max-h-[500px] opacity-100 px-6 pb-4' : 'max-h-0 opacity-0'}`}
    >
      {children}
    </div>
  )
}

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent } 