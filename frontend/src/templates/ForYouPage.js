import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Typography, Button } from '@mui/material';
import Carousel from '../components/Carousel/Carousel';

export function ForYou() {
  const [favorites, setFavorites] = useState([]);
  const [recommendations, setRecommendations] = useState({});
  const [error, setError] = useState('');
  const navigate = useNavigate();
  
  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    if (!storedUser || !storedUser.id) {
      navigate('/login');
      return;
    }
    const userId = storedUser.id;
    
    const fetchFavorites = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/favorites?user_id=${userId}`);
        setFavorites(response.data);
      } catch (err) {
        setError(err.response?.data?.error || 'An error occurred while fetching favorites.');
      }
    };
    
    fetchFavorites();
  }, [navigate]);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (favorites.length === 0) return;
      
      try {
        const selectedFavorites = favorites.sort(() => Math.random() - 0.5).slice(0, 10);
        const recommendationsMap = {};
        await Promise.all(selectedFavorites.map(async (fav) => {
          const response = await axios.post('http://localhost:5000/recommendations', { titles: [fav.title] });
          recommendationsMap[fav.title] = response.data
            .map(item => ({ ...item, contentType: item.type }))
            .sort(() => Math.random() - 0.5);
        }));
        setRecommendations(recommendationsMap);
      } catch (err) {
        setError(err.response?.data?.error || 'An error occurred while fetching recommendations.');
      }
    };
    
    fetchRecommendations();
  }, [favorites]);

  return (
    <>
      <Container style={{ paddingBottom: '100px' }}>
        <Typography variant="h4" style={{ marginTop: '20px', marginBottom: '40px' }}>
          Personalized Recommendations Based on Your Favorites
        </Typography>
  
        {/* No Favorites Message */}
        {favorites.length === 0 && !error ? (
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <Typography variant="h6">You should add some likes on the Showcase page!</Typography>
            <Button variant="contained" color="primary" onClick={() => navigate('/showcase')}>
              Go to Showcase
            </Button>
          </div>
        ) : (
          Object.keys(recommendations).map((favTitle) => {
            const firstItem = recommendations[favTitle][0];
            const itemType = firstItem?.contentType ? firstItem.contentType : 'item';
  
            return (
              recommendations[favTitle].length > 0 && (
                <div key={favTitle} style={{ marginBottom: '40px' }}>
                  <Typography variant="h6" style={{ textAlign: 'left', marginTop: '20px', marginBottom: '10px' }}>
                    Because you liked the {itemType} {favTitle}, here's something similar:
                  </Typography>
                  <Carousel recommendations={recommendations[favTitle]} />
                </div>
              )
            );
          })
        )}
  
        {/* Error Message */}
        {error && (
          <Typography style={{ textAlign: 'center', margin: '20px' }}>
            {error}
          </Typography>
        )}
      </Container>
    </>
  );  
}

export default ForYou;
