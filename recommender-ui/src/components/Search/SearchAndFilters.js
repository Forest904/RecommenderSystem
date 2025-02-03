import React, { useState } from 'react';
import {
  Grid,
  TextField,
  MenuItem,
  List,
  ListItem,
  ListItemButton,
  ListItemText
} from '@mui/material';

const SearchAndFilters = ({ 
  searchQuery, 
  setSearchQuery, 
  sortBy, 
  setSortBy,
  contentType,
  setContentType 
}) => {
  const [suggestions, setSuggestions] = useState([]);

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

  return (
    <Grid container spacing={2} alignItems="center" sx={{ mt: 3, mb: 2 }}>
      <Grid item xs={8}>
        <TextField
          fullWidth
          label="Search"
          variant="outlined"
          value={searchQuery}
          onChange={handleSearchChange}
          onKeyDown={handleKeyDown}
        />
        {suggestions.length > 0 && (
          <List sx={{ position: 'absolute', backgroundColor: 'white', boxShadow: 3, zIndex: 10 }}>
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
      <Grid item xs={2}>
        <TextField
          select
          fullWidth
          label="Content Type"
          value={contentType}
          onChange={(e) => setContentType(e.target.value)}
        >
          <MenuItem value="">All</MenuItem>
          <MenuItem value="movie">Movie</MenuItem>
          <MenuItem value="book">Book</MenuItem>
        </TextField>
      </Grid>
    </Grid>
  );
};

export default SearchAndFilters;
