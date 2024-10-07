import { useState, useEffect } from 'react';

const PasswordManager = () => {
  const [website, setWebsite] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwords, setPasswords] = useState([]);

  const handleAddPassword = async () => {
    const response = await fetch('http://localhost:5000/add-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ website, username, password }),
    });

    const data = await response.json();
    if (data.success) {
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
