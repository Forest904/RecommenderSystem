import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Grid, Container, Typography, CircularProgress } from '@mui/material';
import Card from '../components/Card/Card';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';

function LibraryPage() {
  const [libraryItems, setLibraryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch library items when the component mounts
    const fetchLibraryItems = async () => {
      try {
        const response = await axios.get('/library', { params: { user_id: 1 } }); // Replace with actual user ID logic
        setLibraryItems(response.data);
      } catch (err) {
        setError('Failed to fetch library items.');
      } finally {
        setLoading(false);
      }
    };

    fetchLibraryItems();
  }, []);

  return (
    <>
      <Header title="User Library" />
      <Container>
        <Typography variant="h4" gutterBottom style={{ marginTop: '20px' }}>
          My Library
        </Typography>
        {loading ? (
          <CircularProgress style={{ margin: '20px auto', display: 'block' }} />
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : libraryItems.length === 0 ? (
          <Typography>No items in your library yet.</Typography>
        ) : (
          <Grid container spacing={3} style={{ marginTop: '20px' }}>
            {libraryItems.map((item) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
                <Card
                  title={item.title}
                  type={item.type}
                  image={item.large_cover_url}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </Container>
      <Footer />
    </>
  );
}

export default LibraryPage;
