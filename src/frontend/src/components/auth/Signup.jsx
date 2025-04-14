import { useState } from 'react'

const Signup = ({ setCurrentPage }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setSuccess(null)

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      setIsLoading(false)
      return
    }

    fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: formData.email,
        password: formData.password
      }),
      credentials: 'include',
      mode: 'cors'
    })
      .then(async response => {
        const data = await response.json()
        if (!response.ok) throw new Error(data.detail || 'Registration failed')
        return data
      })
      .then(data => {
        setSuccess('Account created successfully! Please login.')
        setTimeout(() => setSuccess(null), 5000) // Auto-clear success message
        setCurrentPage('login')
      })
      .catch(error => {
        setError(error.message)
      })
      .finally(() => {
        setIsLoading(false)
      })
  }

  return (
    <div className="min-h-[calc(100vh-79px)] bg-[#EEEEEE] flex items-center justify-center px-4">
      <div className="w-full max-w-[480px] bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold font-mono text-center mb-6">Sign Up</h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 font-mono">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4 font-mono">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="block font-mono text-sm font-medium text-[#030303]">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              className="w-full px-3 py-2 border rounded-md font-mono text-[#030303] focus:outline-none focus:ring-2 focus:ring-primary"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="block font-mono text-sm font-medium text-[#030303]">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              className="w-full px-3 py-2 border rounded-md font-mono text-[#030303] focus:outline-none focus:ring-2 focus:ring-primary"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="confirmPassword" className="block font-mono text-sm font-medium text-[#030303]">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              className="w-full px-3 py-2 border rounded-md font-mono text-[#030303] focus:outline-none focus:ring-2 focus:ring-primary"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-2 px-4 rounded-[22.5px] font-mono font-semibold transition-colors ${
              isLoading
                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                : "bg-[#030303] text-white hover:bg-primary"
            }`}
          >
            {isLoading ? 'Signing up...' : 'Sign Up'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="font-mono text-sm text-[#8E8E8E]">
            Already have an account?{' '}
            <button onClick={() => setCurrentPage('login')} className="text-primary hover:underline font-semibold">
              Login
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Signup
