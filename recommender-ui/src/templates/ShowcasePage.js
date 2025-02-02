import React, { useEffect, useState } from 'react';
import { Grid, Container, Typography, Button, TextField, MenuItem, List, ListItem, ListItemButton, ListItemText } from '@mui/material';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';
import Card from '../components/Card/Card';

const ShowcasePage = () => {
    const [content, setContent] = useState([]);
    const [page, setPage] = useState(1);
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('title');
    const [suggestions, setSuggestions] = useState([]);

    useEffect(() => {
        fetch(`http://localhost:5000/content?page=${page}&search_query=${encodeURIComponent(searchQuery.trim())}&sort_by=${sortBy}`)
            .then(res => res.json())
            .then(data => {
                console.log("API Response:", data);
                setContent(data);
            })
            .catch(err => console.error("Fetch Error:", err));
    }, [page, searchQuery, sortBy]);

    const fetchSuggestions = (query) => {
        if (!query) {
            setSuggestions([]);
            return;
        }
        fetch(`http://localhost:5000/search_suggestions?query=${query}`)
            .then(res => res.json())
            .then(data => setSuggestions(data))
            .catch(err => console.error("Suggestion Fetch Error:", err));
    };

    const handleSearchChange = (e) => {
        const value = e.target.value;
        setSearchQuery(value);
        fetchSuggestions(value);
    };

    const handleSuggestionClick = (suggestion) => {
        setSearchQuery(suggestion);
        setSuggestions([]);
    };

    return (
        <>
            <Header />
            <Container>
                {/* Search and Filter Controls */}
                <Grid container spacing={2} alignItems="center" sx={{ marginBottom: 2, marginTop: 3 }}>
                    <Grid item xs={10}>
                        <TextField
                            fullWidth
                            label="Search"
                            variant="outlined"
                            value={searchQuery}
                            onChange={handleSearchChange}
                        />
                        {/* Search Suggestions */}
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
                </Grid>
                
                {/* Movies & Books Section */}
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <Typography variant="h5" gutterBottom>Movies</Typography>
                    </Grid>
                    {content.filter(item => item.type === "Movie").map(({ title, large_cover_url }, index) => (
                        <Grid item xs={3} key={index}>
                            <Card title={title} image={large_cover_url} />
                        </Grid>
                    ))}
                    
                    <Grid item xs={12}>
                        <Typography variant="h5" gutterBottom>Books</Typography>
                    </Grid>
                    {content.filter(item => item.type === "Book").map(({ title, large_cover_url }, index) => (
                        <Grid item xs={3} key={index}>
                            <Card title={title} image={large_cover_url} />
                        </Grid>
                    ))}
                </Grid>
                
                {/* Pagination Controls */}
                <Grid container justifyContent="center" spacing={2} sx={{ marginTop: 2 }}>
                    <Button 
                        variant="contained" 
                        disabled={page === 1} 
                        onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                    >
                        Previous Page
                    </Button>
                    <Button 
                        variant="contained" 
                        onClick={() => setPage(prev => prev + 1)}
                    >
                        Next Page
                    </Button>
                </Grid>
            </Container>
            <Footer />
        </>
    );
};

export default ShowcasePage;
