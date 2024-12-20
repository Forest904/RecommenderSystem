import React, { useState } from 'react';
import axios from 'axios';

export function Users() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState(''); 
  const [userMessage, setUserMessage] = useState('');
  const [error, setError] = useState('');

  const handleCreateUser = async () => {
    try {
      const response = await axios.post('http://localhost:5000/create_user', {
        username,
        email,
        password,
      });
      setUserMessage(response.data.message);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while creating the user.');
      setUserMessage('');
    }
  };

  return (
    <div>
      <h2>Create User</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleCreateUser}>Create User</button>
      {userMessage && <p>{userMessage}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}
