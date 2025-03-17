import { useState } from 'react'

const Signup = ({ setCurrentPage }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    // TODO: Implement signup logic
    // First check if passwords match
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    // Call the register API endpoint
    fetch('http://localhost:8000/api/register/', {
      method: 'POST',
      headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': 'http://localhost:3000',
      'Access-Control-Allow-Methods': 'POST',
      'Access-Control-Allow-Headers': 'Content-Type',
      },
      body: JSON.stringify({
      username: formData.email,
      email: formData.email,
      password: formData.password,
      }),
    })
    .then(response => {
      if (!response.ok) {
      throw new Error('Registration failed');
      }
      return response.json();
    })
    .then(data => {
      console.log('Registration successful:', data);
      alert('Account created successfully! Please login.');
      setCurrentPage('login');
    })
    .catch(error => {
      console.error('Registration error:', error);
      alert('Registration failed. Please try again.');
    });
    console.log('Signup attempt:', formData)
  }

  return (
    <div className="min-h-[calc(100vh-79px)] bg-[#EEEEEE] flex items-center justify-center px-4">
      <div className="w-full max-w-[480px] bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold font-mono text-center mb-8">
          Sign Up
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label 
              htmlFor="email" 
              className="block font-mono text-sm font-medium text-[#030303]"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              className="w-full px-3 py-2 border rounded-md font-mono text-[#030303] focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <label 
              htmlFor="password" 
              className="block font-mono text-sm font-medium text-[#030303]"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              className="w-full px-3 py-2 border rounded-md font-mono text-[#030303] focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <label 
              htmlFor="confirmPassword" 
              className="block font-mono text-sm font-medium text-[#030303]"
            >
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              className="w-full px-3 py-2 border rounded-md font-mono text-[#030303] focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
            />
          </div>

          <button
            type="submit"
            className="w-full bg-[#CCCCCC] hover:bg-primary text-[#030303] hover:text-white font-mono font-semibold py-2 rounded-[22.5px] transition-colors"
          >
            Sign Up
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="font-mono text-sm text-[#8E8E8E]">
            Already have an account?{' '}
            <button
              onClick={() => setCurrentPage('login')}
              className="text-primary hover:underline font-semibold"
            >
              Login
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Signup 