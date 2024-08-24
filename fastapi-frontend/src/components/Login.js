// src/components/Login.js
import React, { useState } from 'react';
import axios from 'axios';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Attempting login with:', { email, password });
    try {
      console.log('Sending request to:', 'http://localhost:8000/auth/login');
      const response = await axios.post('http://localhost:8000/auth/login', { email, password });
      console.log('Login response:', response.data);
      // Handle successful login
      const { access_token, token_type: _token_type } = response.data;
      localStorage.setItem('token', access_token);
      console.log('Token stored in localStorage');
      // Redirect or update UI here
    } catch (error) {
      console.error('Login error:', error.response ? error.response.data : error.message);
      // Handle login error (e.g., show error message)
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
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
      <button type="submit">Login</button>
    </form>
  );
}

export default Login;