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
        <Grid2 container spacing={2} marginTop={4} alignItems="center" justifyContent="center">
          <Grid2 item xs={12} sm={8} md={6}>
            <TextField
              label="Search for a title"
              variant="outlined"
              fullWidth
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </Grid2>
          <Grid2 item xs={12} sm={4} md={2}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleSearch}
            >
              Search
            </Button>
          </Grid2>
        </Grid2>

        {/* Carousel */}
        {recommendations.length > 0 ? (
          <Carousel recommendations={recommendations} />
        ) : (
          <Typography style={{ textAlign: "center", margin: "20px" }}>
            No valid recommendations available.
          </Typography>
        )}
      </Container>
    </>
  );
};

export default App;
