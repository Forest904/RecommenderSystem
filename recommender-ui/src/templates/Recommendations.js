import React, { useState } from 'react';
import axios from 'axios';
import { Container, Typography } from '@mui/material';
import Carousel from '../components/Carousel/Carousel';
import SearchBar from '../components/Forms/SearchBar';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';

export function Recommendations() {
  const [contentTitle, setContentTitle] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');

  const handleGetRecommendations = async () => {
    try {
      const response = await axios.post('http://localhost:5000/recommendations', {
        title: contentTitle,
      });
      setRecommendations(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while fetching recommendations.');
      setRecommendations([]);
    }
  };

  const books = recommendations.filter(item => item.type === 'book');
  const movies = recommendations.filter(item => item.type === 'movie');

  return (
    <>
      <Header title="Recommendations by title" />
      <Container>
        {/* Search Bar */}
        <SearchBar
          searchQuery={contentTitle}
          setSearchQuery={setContentTitle}
          handleSearch={handleGetRecommendations}
        />
  
        {/* Carousel for Movies */}
        {movies.length > 0 && (
          <>
            <Typography variant="h6" style={{ textAlign: "center", marginTop: "20px" }}>Movies</Typography>
            <Carousel recommendations={movies} />
          </>
        )}

        {/* Carousel for Books */}
        {books.length > 0 && (
          <>
            <Typography variant="h6" style={{ textAlign: "center", marginTop: "20px" }}>Books</Typography>
            <Carousel recommendations={books} />
          </>
        )}

        {/* Error Message */}
        {error && (
          <Typography style={{ textAlign: "center", margin: "20px" }}>
            {error}
          </Typography>
        )}
      </Container>
      <Footer />
    </>
  );
}

export default Recommendations;
