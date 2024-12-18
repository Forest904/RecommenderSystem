import React, { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  TextField,
  Button,
  Card,
  CardMedia,
  CardContent,
  Grid,
  Container,
} from "@mui/material";
import Carousel from "react-material-ui-carousel";
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
      <AppBar position="static" style={{ marginBottom: "20px" }}>
        <Toolbar>
          <Typography variant="h6" style={{ flexGrow: 1 }}>
            Recommendation App
          </Typography>
        </Toolbar>
      </AppBar>

      <Container>
        {/* Search Bar */}
        <Grid container spacing={2} alignItems="center" justifyContent="center">
          <Grid item xs={12} sm={8} md={6}>
            <TextField
              label="Search for a title"
              variant="outlined"
              fullWidth
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={4} md={2}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleSearch}
            >
              Search
            </Button>
          </Grid>
        </Grid>

        {/* Carousel */}
        {recommendations.length > 0 ? (
          <Carousel navButtonsAlwaysVisible style={{ marginTop: "30px" }}>
            {recommendations.map((item, index) => (
              <Grid container spacing={2} justifyContent="center" key={index}>
                <Grid item xs={12} sm={6} md={4} lg={3}>
                  <Card style={{ height: "100%" }}>
                    <CardMedia
                      component="img"
                      height="200"
                      image={item.image_url || "https://via.placeholder.com/150"}
                      alt={item.Title}
                      style={{ objectFit: "cover" }}
                    />
                    <CardContent>
                      <Typography
                        variant="subtitle1"
                        noWrap
                        style={{ textAlign: "center" }}
                      >
                        {item.Title}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            ))}
          </Carousel>
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
