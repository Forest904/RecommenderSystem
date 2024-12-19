import React from "react";
import PropTypes from "prop-types";
import { TextField, Button, Grid2 } from "@mui/material";

const SearchBar = ({ searchQuery, setSearchQuery, handleSearch }) => {
  return (
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
  );
};

SearchBar.propTypes = {
  searchQuery: PropTypes.string.isRequired,
  setSearchQuery: PropTypes.func.isRequired,
  handleSearch: PropTypes.func.isRequired,
};

export default SearchBar;
