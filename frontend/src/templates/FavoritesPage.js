import React, { useEffect, useState } from 'react';
import {
  Grid,
  Container,
  Typography,
  Box,
  Button,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card/Card';

const FavoritesPage = () => {
  const [favorites, setFavorites] = useState([]);
  const [userId, setUserId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    if (storedUser && storedUser.id) {
      setUserId(storedUser.id);
    } else {
      navigate('/login');
    }
  }, [navigate]);

  useEffect(() => {
    if (userId) {
      fetch(`http://localhost:5000/favorites?user_id=${userId}`)
        .then((res) => res.json())
        .then((data) => {
          console.log('Favorites:', data);
          setFavorites(data);
        })
        .catch((err) => console.error('Fetch Favorites Error:', err));
    }
  }, [userId]);

  const handleUnlike = (contentId) => {
    if (!userId) return;

    fetch('http://localhost:5000/favorites', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, content_id: contentId }),
    })
      .then((res) => {
        if (res.ok) {
          setFavorites((prevFavorites) => prevFavorites.filter(item => item.id !== contentId));
        } else {
          console.error("Error removing favorite");
        }
      })
      .catch((err) => console.error('Error updating favorites:', err));
  };

  const hasFavorites = favorites.length > 0;

  return (
    <>
      <Container sx={{ minHeight: 'calc(100vh - 160px)', paddingBottom: '80px', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h4" gutterBottom sx={{ marginTop: 3, fontWeight: 'bold' }}>
          Your Favorite Movies & Books
        </Typography>
        {!hasFavorites ? (
          <Box sx={{ textAlign: 'center', marginTop: 10 }}>
            <Typography variant="h5" gutterBottom>No Favorites Yet</Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              You haven’t added any favorites. Explore movies and books to start your collection!
            </Typography>
            <Button variant="contained" color="primary" onClick={() => navigate('/')}>Explore Content</Button>
          </Box>
        ) : (
          <Grid container spacing={2} sx={{ flexGrow: 1, mt: 3, mb: 10 }}>
            <Grid item xs={6} sx={{ borderRight: '1px solid gray' }}>
              <Typography variant="h5" gutterBottom>Movies</Typography>
              <Grid container spacing={2}>
                {favorites.filter((item) => item.type === 'Movie').map((item, index) => (
                  <Grid item xs={6} key={index}>
                    <Card 
                      title={item.title} 
                      image={item.large_cover_url} 
                      contentId={item.id}
                      link={item.link}
                      userId={userId}
                      isLiked={true}
                      onLikeToggle={() => handleUnlike(item.id)}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="h5" gutterBottom>Books</Typography>
              <Grid container spacing={2}>
                {favorites.filter((item) => item.type === 'Book').map((item, index) => (
                  <Grid item xs={6} key={index}>
                    <Card 
                      title={item.title} 
                      image={item.large_cover_url} 
                      contentId={item.id}
                      link={item.link}
                      userId={userId}
                      isLiked={true}
                      onLikeToggle={() => handleUnlike(item.id)}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
          </Grid>
        )}
      </Container>
    </>
  );
};

export default FavoritesPage;
