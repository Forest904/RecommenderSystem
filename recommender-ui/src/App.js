// src/App.js
import React from "react";
import { Container, AppBar, Typography, TextField, Grid, Card, CardContent, CardMedia, Button } from "@mui/material";
import { useState } from "react";

const App = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]); // Placeholder for fetched results

  const handleSearch = () => {
    // Mock function: Replace with API call
    setResults([
      {
        type: "movie",
        title: "The Matrix",
        description: "A hacker discovers the shocking truth about his world.",
        image: "https://via.placeholder.com/150"
      },
      {
        type: "book",
        title: "1984",
        description: "A dystopian novel about surveillance and control.",
        image: "https://via.placeholder.com/150"
      }
    ]);
  };

  return (
    <Container>
      <AppBar position="static" color="primary">
        <Typography variant="h4" align="center" sx={{ padding: 2 }}>
          Recommender System
        </Typography>
      </AppBar>
      <Container sx={{ marginTop: 4 }}>
        <TextField
          label="Enter Movie or Book Title"
          variant="outlined"
          fullWidth
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button
          variant="contained"
          color="primary"
          sx={{ marginTop: 2 }}
          onClick={handleSearch}
        >
          Search
        </Button>
        <Grid container spacing={3} sx={{ marginTop: 4 }}>
          {results.map((result, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardMedia
                  component="img"
                  alt={result.title}
                  height="150"
                  image={result.image}
                />
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {result.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {result.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Container>
  );
};

export default App;
