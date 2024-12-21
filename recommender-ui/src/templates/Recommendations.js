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
  
        {/* Carousel */}
        {recommendations.length > 0 ? (
          <Carousel recommendations={recommendations} />
        ) : (
          <Typography style={{ textAlign: "center", margin: "20px" }}>
            {error || "No valid recommendations available."}
          </Typography>
        )}
      </Container>
      <Footer />
    </>
  );
  
}

export default Recommendations;


