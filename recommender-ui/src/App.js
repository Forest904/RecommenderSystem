import React, { useState, useEffect } from "react";
import {
  Typography,
  TextField,
  Button,
  Container,
  Grid2,
} from "@mui/material";
import Header from './components/Header/Header';
import Carousel from './components/Carousel/Carousel';
import SearchBar from './components/Forms/SearchBar';
import Footer from './components/Footer/Footer';
import axios from "axios";

const App = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [recommendations, setRecommendations] = useState([]);

  const handleSearch = () => {
    if (searchQuery) {
      axios
        .post("http://localhost:5000/recommendations", { title: searchQuery })
        .then((response) => {
          console.log("API Response:", response.data); // Log API response
          setRecommendations(response.data || []);
        })
        .catch((error) => {
          console.error("Error fetching recommendations:", error);
          setRecommendations([]);
        });
    }
  };

  useEffect(() => {
    // Preload some recommendations (optional)
  }, []);

  return (
    <>
      {/* Header */}
      <Header />

      <Container>
        {/* Search Bar */}
        <SearchBar
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          handleSearch={handleSearch}
        />

        {/* Carousel */}
        {recommendations.length > 0 ? (
          <Carousel recommendations={recommendations} />
        ) : (
          <Typography style={{ textAlign: "center", margin: "20px" }}>
            No valid recommendations available.
          </Typography>
        )}
      </Container>

      {/* Footer */}
      <Footer />
    </>
  );
};

export default App;
