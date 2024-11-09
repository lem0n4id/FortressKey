import { useState } from 'react';
import Register from './components/Register';
import Login from './components/Login';
import PasswordManager from './components/PasswordManager';

function App() {
  const [loggedIn, setLoggedIn] = useState(() => {
    try {
      // Initialize state from sessionStorage
      const sessionCookie = document.cookie.split(';').find(c => c.trim().startsWith('session_id=')).trim();
      return sessionCookie ? true : false;
    } catch (error) {
      return false;
    }
  });

  const [activeTab, setActiveTab] = useState('login'); // State to manage active tab

  return (
    <div className="App min-h-screen flex items-center justify-center bg-gray-100 p-4">
      {!loggedIn ? (
        <div className="w-full max-w-md p-6 bg-white rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold text-center text-gray-700 mb-6">Password Manager</h1>

          {/* Tab navigation */}
          <div className="flex justify-center mb-4">
            <button
              onClick={() => setActiveTab('login')}
              className={`px-4 py-2 w-full text-center rounded-t-lg ${activeTab === 'login' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-600'} transition duration-300`}
            >
              Login
            </button>
            <button
              onClick={() => setActiveTab('register')}
              className={`px-4 py-2 w-full text-center rounded-t-lg ${activeTab === 'register' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-600'} transition duration-300`}
            >
              Register
            </button>
          </div>

          {/* Tab content */}
          {activeTab === 'login' && <Login setLoggedIn={setLoggedIn} />}
          {activeTab === 'register' && <Register />}
        </div>
      ) : (
        <div className="w-full max-w-2xl p-6 bg-white rounded-lg shadow-lg">
          <PasswordManager />
        </div>
      )}
    </div>
  );
}

export default App;
