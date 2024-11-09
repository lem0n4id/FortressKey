import { useState, useEffect } from 'react';
import 'cross-fetch/polyfill';

const PasswordManager = () => {
  const [website, setWebsite] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwords, setPasswords] = useState([]);

  const fetchPasswords = async () => {
    const headers = {
      'Content-Type': 'application/json'
    };

    const sessionCookie = document.cookie.split(';').find(c => c.trim().startsWith('session_id=')).trim();
    if (sessionCookie) {
      headers['Cookie'] = sessionCookie;
    }

    const response = await fetch('http://localhost:5000/get-passwords', {
      method: 'GET',
      headers,
      credentials: 'include'
    });
    const data = await response.json();
    setPasswords(data.passwords);
  };

  const handleAddPassword = async () => {
    const headers = {
      'Content-Type': 'application/json'
    };

    const sessionCookie = document.cookie.split(';').find(c => c.trim().startsWith('session_id='));
    if (sessionCookie) {
      headers['Cookie'] = sessionCookie.trim();
    }

    const response = await fetch('http://localhost:5000/add-password', {
      method: 'POST',
      headers,
      body: JSON.stringify({ website, username, password }),
      credentials: 'include'
    });

    const data = await response.json();
    if (data) {
      fetchPasswords(); // Update password list after adding
      // Clear the input fields
      setWebsite('');
      setUsername('');
      setPassword('');

    }
  };

  const handleLogout = () => {
    // Clear the session_id cookie by setting it to expire in the past
    document.cookie = "session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    setPasswords([]); // Clear passwords from the state as well
    alert("Logged out successfully.");
    window.location.reload(); // Reload the page to reset the app state
  };

  useEffect(() => {
    fetchPasswords(); // Fetch passwords on component mount
  }, []);

  return (
    <div className="max-w-lg mx-auto mt-10 p-6 bg-gray-100 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-700">Password Manager</h2>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white font-semibold py-2 px-4 rounded-lg hover:bg-red-600 transition duration-300"
        >
          Logout
        </button>
      </div>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Website"
          value={website}
          onChange={(e) => setWebsite(e.target.value)}
          className="w-full p-3 mb-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-3 mb-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          onClick={handleAddPassword}
          className="w-full bg-indigo-600 text-white font-semibold p-3 rounded-lg hover:bg-indigo-700 transition duration-300"
        >
          Add Password
        </button>
      </div>

      <h3 className="text-xl font-semibold text-gray-600 mt-8 mb-4">Stored Passwords</h3>
      <table className="min-w-full bg-white border rounded-lg overflow-hidden">
        <thead>
          <tr className="bg-indigo-200 text-gray-700 text-left">
            <th className="p-3 font-semibold">Website</th>
            <th className="p-3 font-semibold">Username</th>
            <th className="p-3 font-semibold">Password</th>
          </tr>
        </thead>
        <tbody>
          {passwords.length > 0 ? (
            passwords.map((entry, index) => (
              <tr key={index} className="border-b last:border-0">
                <td className="p-3 text-gray-700">{entry.website}</td>
                <td className="p-3 text-gray-700">{entry.username}</td>
                <td className="p-3 text-gray-700">{entry.password}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="3" className="p-3 text-gray-500 text-center">No passwords stored</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default PasswordManager;
