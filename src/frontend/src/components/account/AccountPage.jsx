import { useState } from "react"
import { User, LogOut, Trash2 } from "lucide-react"

const AccountPage = ({ setCurrentPage, setIsLoggedIn }) => {
  const [isEditingProfile, setIsEditingProfile] = useState(false)
  const [formData, setFormData] = useState({
    name: "John Doe",
    email: "john.doe@example.com",
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const accessToken = localStorage.getItem('accessToken')


  // Fetch user profile data when component mounts
  useState(() => {
    const fetchProfile = async () => {
      try {
        setIsLoading(true)
        const response = await fetch('http://localhost:8000/api/users/profile/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          credentials: 'include'
        })
  
        if (!response.ok) {
          throw new Error('Not authenticated or server error')
        }
        
        const data = await response.json()
        if (data.status === 'success') {
          setFormData({
            ...formData,
            name: data.user.name || "User",
            email: data.user.email || ""
          })
        }
      } catch (err) {
        console.error('Error fetching profile:', err)
        setError('Could not load profile data')
        // Redirect to login if not authenticated
        setIsLoggedIn(false)
        setCurrentPage('login')
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchProfile()
  }, [])

  const handleLogout = () => {
    setIsLoggedIn(false)
    setCurrentPage('login')
  }

  const handleDeleteAccount = () => {
    setIsLoggedIn(false)
    setCurrentPage('login')
  }

  return (
    <div className="min-h-[calc(100vh-79px)] bg-[#EEEEEE] p-4">
      <div className="max-w-[960px] mx-auto space-y-6">
        {/* Profile Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold font-mono mb-6">User Profile</h2>
          {isLoading ? (
            <p className="text-center py-4">Loading profile data...</p>
          ) : error ? (
            <p className="text-center py-4 text-red-500">{error}</p>
          ) : (
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 bg-[#030303] rounded-full flex items-center justify-center">
                <User size={40} className="text-white" />
              </div>
              <div className="flex-1">
                {isEditingProfile ? (
                  <div className="space-y-4">
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md font-mono"
                    />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md font-mono"
                    />
                  </div>
                ) : (
                  <div>
                    <h3 className="text-xl font-mono">{formData.name}</h3>
                    <p className="text-gray-600 font-mono">{formData.email}</p>
                  </div>
                )}
              </div>
              <button
                onClick={() => setIsEditingProfile(!isEditingProfile)}
                className="bg-[#CCCCCC] hover:bg-primary text-[#030303] hover:text-white px-6 py-2 rounded-[22.5px] font-mono font-semibold transition-colors"
              >
                {isEditingProfile ? "Save" : "Edit Profile"}
              </button>
            </div>
          )}
        </div>

        {/* Password Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold font-mono mb-6">Change Password</h2>
          <div className="space-y-4">
            <div>
              <label className="block font-mono mb-2">Current Password</label>
              <input
                type="password"
                className="w-full px-3 py-2 border rounded-md font-mono"
                value={formData.currentPassword}
                onChange={(e) => setFormData({ ...formData, currentPassword: e.target.value })}
              />
            </div>
            <div>
              <label className="block font-mono mb-2">New Password</label>
              <input
                type="password"
                className="w-full px-3 py-2 border rounded-md font-mono"
                value={formData.newPassword}
                onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
              />
            </div>
            <div>
              <label className="block font-mono mb-2">Confirm New Password</label>
              <input
                type="password"
                className="w-full px-3 py-2 border rounded-md font-mono"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              />
            </div>
            <button className="bg-[#CCCCCC] hover:bg-primary text-[#030303] hover:text-white px-6 py-2 rounded-[22.5px] font-mono font-semibold transition-colors">
              Update Password
            </button>
          </div>
        </div>

        {/* Account Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold font-mono mb-6">Account Actions</h2>
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleLogout}
              className="flex items-center justify-center gap-2 bg-[#CCCCCC] hover:bg-primary text-[#030303] hover:text-white px-6 py-2 rounded-[22.5px] font-mono font-semibold transition-colors"
            >
              <LogOut size={20} />
              <span>Log Out</span>
            </button>
            <button
              onClick={handleDeleteAccount}
              className="flex items-center justify-center gap-2 border border-red-500 text-red-500 hover:bg-red-500 hover:text-white px-6 py-2 rounded-[22.5px] font-mono font-semibold transition-colors"
            >
              <Trash2 size={20} />
              <span>Delete Account</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AccountPage 