import { useState } from "react";

const Login = ({ setCurrentPage, setIsLoggedIn }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement actual login logic

    // Call the login API endpoint
    console.log("Attempting to login with:", formData.email);

    // Use fetch to call the backend API
    fetch("http://localhost:8000/api/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "http://localhost:3000",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type",
      },
      body: JSON.stringify({
        username: formData.email,
        password: formData.password,
      }),
      credentials: "include",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Login failed");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Login successful:", data);
        // Set login state and redirect only if login was successful
        setIsLoggedIn(true);
        setCurrentPage("dashboard");
      })
      .catch((error) => {
        console.error("Login error:", error);
        alert("Login failed. Please check your credentials and try again.");
        // Don't set login state or redirect on failure
        setIsLoggedIn(false);
      });

    // Prevent the default form submission which was doing unconditional login
    // return;

    // setIsLoggedIn(true)
    // setCurrentPage('dashboard')
  };

  return (
    <div className="min-h-[calc(100vh-79px)] bg-[#EEEEEE] flex items-center justify-center px-4">
      <div className="w-full max-w-[480px] bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold font-mono text-center mb-8">Login</h1>

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
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
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
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
            />
          </div>

          <button
            type="submit"
            className="w-full bg-[#CCCCCC] hover:bg-primary text-[#030303] hover:text-white font-mono font-semibold py-2 rounded-[22.5px] transition-colors"
          >
            Login
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
