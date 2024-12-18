import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [title, setTitle] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setRecommendations([]);

    try {
      const response = await axios.post('http://127.0.0.1:5000/recommendations', { title });
    
      if (Array.isArray(response.data)) {
        // Success case: response is an array of recommendations
        setRecommendations(response.data);
      } else if (response.data && response.data.error) {
        // Server-side error returned as { "error": "..." }
        setError(response.data.error);
      } else {
        // Unknown response structure
        setError('Unexpected response format from the server.');
      }
    } catch (err) {
      // Network or Axios error
      if (err.response) {
        setError(err.response.data.error || 'Something went wrong.');
      } else {
        setError('Failed to fetch recommendations.');
      }
    }
  };

  return (
    <div>
      <h1>Recommender System</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter content title"
        />
        <button type="submit">Get Recommendations</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div>
        <h2>Recommendations</h2>
        {Array.isArray(recommendations) && recommendations.length > 0 ? (
          recommendations.map((rec, index) => (
            <div key={index}>
              <h3>{rec.Title}</h3>
              <p>{rec.Type}</p>
              {rec.image_url && <img src={rec.image_url} alt={rec.Title} />}
            </div>
          ))
        ) : (
          <p>No recommendations available.</p>
        )}
      </div>
    </div>
  );
};

export default App;
