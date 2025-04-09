import { useState } from "react";

const Login = ({ setCurrentPage, setIsLoggedIn }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    console.log("Attempting to login with:", formData.email);
    
    const formBody = new URLSearchParams();
    formBody.append('username', formData.email);
    formBody.append('password', formData.password);
    
    fetch("http://localhost:8000/api/auth/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formBody,
      credentials: 'include',
      mode: 'cors'
    })
    .then(async (response) => {
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Login failed");
      }
      return response.json();
    })
    .then((data) => {
      console.log("Login successful:", data);
      localStorage.setItem('accessToken', data.access_token);
      setIsLoggedIn(true);
      setCurrentPage("dashboard");
    })
    .catch((error) => {
      console.error("Login error:", error);
      setError(error.message);
    })
    .finally(() => {
      setIsLoading(false);
    });
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-3xl font-bold font-mono text-center mb-6">
          Log In
        </h1>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
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
              name="email"
              type="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md font-mono"
              placeholder="your.email@example.com"
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
              name="password"
              type="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md font-mono"
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
            {isLoading ? "Logging in..." : "Log In"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="font-mono text-sm text-[#8E8E8E]">
            Don't have an account?{" "}
            <button
              onClick={() => setCurrentPage("signup")}
              className="text-primary hover:underline font-semibold"
            >
              Sign Up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
