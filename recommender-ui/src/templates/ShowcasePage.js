import React, { useEffect, useState, useRef } from 'react';
import { Grid, Container, Typography, Button, Box } from '@mui/material';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';
import Card from '../components/Card/Card';
import SearchAndFilters from '../components/Search/SearchAndFilters';

const ShowcasePage = () => {
  const [content, setContent] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('title');
  const [contentType, setContentType] = useState(''); // '' means both types, or 'movie'/'book'
  const [userId, setUserId] = useState(null);
  const footerRef = useRef(null);
  const [footerInView, setFooterInView] = useState(false);

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    if (storedUser && storedUser.id) {
      setUserId(storedUser.id);
      console.log("Current User ID:", storedUser.id);
    }
  }, []);

  useEffect(() => {
    // Include the content_type parameter in the query string.
    fetch(
      `http://localhost:5000/content?page=${page}&search_query=${encodeURIComponent(
        searchQuery.trim()
      )}&sort_by=${sortBy}&content_type=${contentType}`
    )
      .then((res) => res.json())
      .then((data) => setContent(data))
      .catch((err) => console.error('Fetch Error:', err));
  }, [page, searchQuery, sortBy, contentType]);

  useEffect(() => {
    if (userId) {
      fetch(`http://localhost:5000/favorites?user_id=${userId}`)
        .then((res) => res.json())
        .then((data) => setFavorites(data.map((item) => item.id)))
        .catch((err) => console.error('Fetch Favorites Error:', err));
    }
  }, [userId]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setFooterInView(entry.isIntersecting),
      { threshold: 0.1 }
    );
    if (footerRef.current) observer.observe(footerRef.current);
    return () => observer.disconnect();
  }, []);

  const handleLikeToggle = (contentId) => {
    if (!userId) return;
    const isLiked = favorites.includes(contentId);
    const method = isLiked ? 'DELETE' : 'POST';

    fetch('http://localhost:5000/favorites', {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, content_id: contentId }),
    })
      .then(() => {
        setFavorites((prevFavorites) =>
          isLiked
            ? prevFavorites.filter((id) => id !== contentId)
            : [...prevFavorites, contentId]
        );
      })
      .catch((err) => console.error('Error updating favorites:', err));
  };

  return (
    <>
      <Header />
      <Container
        sx={{
          minHeight: 'calc(100vh - 160px)',
          paddingBottom: '80px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <Typography variant="h4" sx={{ textAlign: 'left', mt: 3, mb: 3 }}>
            Cinema & Literature Showcase
        </Typography>
        <SearchAndFilters 
          searchQuery={searchQuery} 
          setSearchQuery={setSearchQuery} 
          sortBy={sortBy} 
          setSortBy={setSortBy} 
          contentType={contentType}
          setContentType={setContentType}
        />
        <Grid container spacing={2} sx={{ flexGrow: 1, mt: 3, mb: 10 }}>
          {(contentType === '' || contentType === 'movie') && (
            <Grid
              item
              xs={contentType === '' ? 6 : 12}
              sx={contentType === '' ? { borderRight: '1px solid gray' } : {}}
            >
              <Typography variant="h5" gutterBottom>Movies</Typography>
              <Grid container spacing={2}>
                {content.filter((item) => item.type === 'Movie').map((item, index) => (
                  <Grid
                    item
                    key={index}
                    sx={{
                      // If only one type is selected, show five cards per row (20% each); otherwise two per row (50%)
                      flexBasis: contentType === '' ? '50%' : '20%',
                      maxWidth: contentType === '' ? '50%' : '20%'
                    }}
                  >
                    <Card 
                      title={item.title} 
                      image={item.large_cover_url} 
                      contentId={item.id}
                      userId={userId}
                      isLiked={favorites.includes(item.id)}
                      onLikeToggle={() => handleLikeToggle(item.id)}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
          )}
          {(contentType === '' || contentType === 'book') && (
            <Grid item xs={contentType === '' ? 6 : 12}>
              <Typography variant="h5" gutterBottom>Books</Typography>
              <Grid container spacing={2}>
                {content.filter((item) => item.type === 'Book').map((item, index) => (
                  <Grid
                    item
                    key={index}
                    sx={{
                      flexBasis: contentType === '' ? '50%' : '20%',
                      maxWidth: contentType === '' ? '50%' : '20%'
                    }}
                  >
                    <Card 
                      title={item.title} 
                      image={item.large_cover_url} 
                      contentId={item.id}
                      userId={userId}
                      isLiked={favorites.includes(item.id)}
                      onLikeToggle={() => handleLikeToggle(item.id)}
                    />
                  </Grid>
                ))}
              </Grid>
            </Grid>
          )}
        </Grid>
        <Box
          sx={{
            marginTop: 'auto',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}
          ref={footerRef}
        >
          <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
            <Footer />
          </Box>
          {footerInView && (
            <Box
              sx={{
                position: 'absolute',
                bottom: 10,
                left: 0,
                right: 0,
                display: 'flex',
                justifyContent: 'center',
                zIndex: 10,
                mt: 2,
                mb: 2
              }}
            >
              <Button
                variant="contained"
                disabled={page === 1}
                onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                sx={{ mx: 2 }}
              >
                Previous Page
              </Button>
              <Button
                variant="contained"
                onClick={() => setPage((prev) => prev + 1)}
                sx={{ mx: 2 }}
              >
                Next Page
              </Button>
            </Box>
          )}
        </Box>
      </Container>
    </>
  );
};

export default ShowcasePage;
