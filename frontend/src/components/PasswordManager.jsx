import { useState, useEffect } from 'react';
import 'cross-fetch/polyfill';

const PasswordManager = () => {
  const [website, setWebsite] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwords, setPasswords] = useState([]);

  const handleAddPassword = async () => {
      const headers = {
        'Content-Type': 'application/json',
          'Cookie': 'session_id=f7515ca3-2b6d-4a00-a851-d4705135f4be',
      };

      console.log(document.cookie)
      // issue here
        {/*
        HttpOnly Flag: If the cookie is set with the HttpOnly flag, it cannot be accessed through JavaScript. This is a security measure to prevent unauthorized access to cookies.
        SameSite Attribute: The SameSite attribute controls whether a cookie is sent to cross-site requests. If set to Strict or Lax, the cookie might not be included in your request because it's considered cross-site.
        */}
      const sessionCookie = document.cookie.split(';').find(c => c.startsWith('session_id='));
      console.log(sessionCookie);
      if (sessionCookie) {
          headers['Cookie'] = sessionCookie;
      }

    const response = await fetch('http://localhost:5000/add-password', {
      method: 'POST',
      headers,
      body: JSON.stringify({ website, username, password }),
    });

    const data = await response.json();
    if (data) {
      fetchPasswords(); // Update password list after adding
    }
  };

  const fetchPasswords = async () => {
    const response = await fetch('http://localhost:5000/get-passwords');
    const data = await response.json();
    setPasswords(data.passwords);
  };

  useEffect(() => {
    fetchPasswords(); // Fetch passwords on component mount
  }, []);

  return (
    <div>
      <h2>Password Manager</h2>
      <input
        type="text"
        placeholder="Website"
        value={website}
        onChange={(e) => setWebsite(e.target.value)}
      />
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleAddPassword}>Add Password</button>

      <h3>Stored Passwords</h3>
      <ul>
        {passwords.map((entry, index) => (
          <li key={index}>
            <strong>{entry.website}</strong> - {entry.username} - {entry.password}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PasswordManager;
