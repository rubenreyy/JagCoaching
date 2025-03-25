const Card = ({ className = '', children }) => {
  return (
    <div className={`bg-white rounded-2xl shadow-md ${className}`}>
      {children}
    </div>
  )
}

const CardHeader = ({ children }) => {
  return <div className="p-6 pb-0">{children}</div>
}

const CardTitle = ({ children }) => {
  return <h3 className="text-2xl font-bold font-mono text-[#030303]">{children}</h3>
}

const CardContent = ({ children }) => {
  return <div className="p-6">{children}</div>
}

export { Card, CardHeader, CardTitle, CardContent } 