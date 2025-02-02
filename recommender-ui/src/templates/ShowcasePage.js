import React, { useEffect, useState, useRef } from 'react';
import {
  Grid,
  Container,
  Typography,
  Button,
  TextField,
  MenuItem,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Box,
} from '@mui/material';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';
import Card from '../components/Card/Card';

const ShowcasePage = () => {
  const [content, setContent] = useState([]);
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('title');
  const [suggestions, setSuggestions] = useState([]);
  const footerRef = useRef(null);
  const [footerInView, setFooterInView] = useState(false);

  useEffect(() => {
    fetch(
      `http://localhost:5000/content?page=${page}&search_query=${encodeURIComponent(
        searchQuery.trim()
      )}&sort_by=${sortBy}`
    )
      .then((res) => res.json())
      .then((data) => {
        console.log('API Response:', data);
        setContent(data);
      })
      .catch((err) => console.error('Fetch Error:', err));
  }, [page, searchQuery, sortBy]);

  const fetchSuggestions = (query) => {
    if (!query) {
      setSuggestions([]);
      return;
    }
    fetch(`http://localhost:5000/search_suggestions?query=${query}`)
      .then((res) => res.json())
      .then((data) => setSuggestions(data))
      .catch((err) => console.error('Suggestion Fetch Error:', err));
  };

  const handleSearchChange = (e) => {
    const value = e.target.value;
    if (value.trim() === '') {
      setSearchQuery('');
      setSuggestions([]);
      return;
    }
    setSearchQuery(value);
    fetchSuggestions(value);
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion);
    setSuggestions([]);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      setSuggestions([]);
    }
  };

  // Intersection Observer to detect when the footer comes into view.
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setFooterInView(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );

    if (footerRef.current) {
      observer.observe(footerRef.current);
    }
    return () => {
      if (footerRef.current) {
        observer.unobserve(footerRef.current);
      }
    };
  }, []);

  return (
    <>
      <Header />
      <Container
        sx={{
          minHeight: 'calc(100vh - 160px)',
          paddingBottom: '80px',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Search and Filter Controls */}
        <Grid container spacing={2} alignItems="center" sx={{ mt: 3, mb: 2 }}>
          <Grid item xs={10}>
            <TextField
              fullWidth
              label="Search"
              variant="outlined"
              value={searchQuery}
              onChange={handleSearchChange}
              onKeyDown={handleKeyDown}
            />
            {/* Search Suggestions */}
            {suggestions.length > 0 && (
              <List
                sx={{
                  position: 'absolute',
                  backgroundColor: 'white',
                  boxShadow: 3,
                  zIndex: 10,
                }}
              >
                {suggestions.map((suggestion, index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemButton onClick={() => handleSuggestionClick(suggestion)}>
                      <ListItemText primary={suggestion} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            )}
          </Grid>
          <Grid item xs={2}>
            <TextField
              select
              fullWidth
              label="Sort By"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <MenuItem value="title">Title</MenuItem>
              <MenuItem value="release">Release Date</MenuItem>
              <MenuItem value="vote_average">Rating</MenuItem>
            </TextField>
          </Grid>
        </Grid>

        {/* Movies & Books - Side by Side */}
        <Grid container spacing={2} sx={{ flexGrow: 1, mt: 3, mb: 10 }}>
          <Grid item xs={6}>
            <Typography variant="h5" gutterBottom>
              Movies
            </Typography>
            <Grid container spacing={2}>
              {content
                .filter((item) => item.type === 'Movie')
                .map(({ title, large_cover_url }, index) => (
                  <Grid item xs={6} key={index}>
                    <Card title={title} image={large_cover_url} />
                  </Grid>
                ))}
            </Grid>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="h5" gutterBottom>
              Books
            </Typography>
            <Grid container spacing={2}>
              {content
                .filter((item) => item.type === 'Book')
                .map(({ title, large_cover_url }, index) => (
                  <Grid item xs={6} key={index}>
                    <Card title={title} image={large_cover_url} />
                  </Grid>
                ))}
            </Grid>
          </Grid>
        </Grid>

        {/* Footer with Pagination Controls Overlaid */}
        <Box
          sx={{
            marginTop: 'auto',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
          ref={footerRef}
        >
          {/* Wrap Footer in a flex Box to center its content */}
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
                mb: 2,
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
