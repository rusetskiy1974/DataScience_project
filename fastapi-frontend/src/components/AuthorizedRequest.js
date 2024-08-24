// src/components/AuthorizedRequest.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AuthorizedRequest() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No token found. Please log in.');
        return;
      }

      try {
        const response = await axios.get('http://localhost:8000/auth/protected', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setData(response.data);
      } catch (err) {
        if (err.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          setError(`Error ${err.response.status}: ${err.response.data.detail || JSON.stringify(err.response.data)}`);
        } else if (err.request) {
          // The request was made but no response was received
          setError('No response received from server');
        } else {
          // Something happened in setting up the request that triggered an Error
          setError('Error setting up the request');
        }
        console.error('Error details:', err);
      }
    };

    fetchData();
  }, []);

  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h2>Authorized Data:</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export default AuthorizedRequest;