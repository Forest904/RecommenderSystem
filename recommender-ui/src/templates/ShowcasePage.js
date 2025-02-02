import React, { useEffect, useState } from 'react';
import { Grid, Container, Typography, Button } from '@mui/material';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';
import Card from '../components/Card/Card';

const ShowcasePage = () => {
    const [content, setContent] = useState([]);
    const [page, setPage] = useState(1);

    useEffect(() => {
        fetch(`http://localhost:5000/content?page=${page}`) // Ensure correct backend URL
            .then(res => res.json())
            .then(data => {
                console.log("API Response:", data);
                setContent(data);
            })
            .catch(err => console.error("Fetch Error:", err));
    }, [page]);

    return (
        <>
            <Header />
            <Container>
                <Grid container spacing={2}>
                    <Grid item xs={6}>
                        <Typography variant="h5" gutterBottom>Movies</Typography>
                        {content.filter(item => item.type === "Movie").map(({ title, large_cover_url }, index) => (
                            <Card
                                key={index}
                                title={title}
                                image={large_cover_url}
                            />
                        ))}
                    </Grid>
                    <Grid item xs={6}>
                        <Typography variant="h5" gutterBottom>Books</Typography>
                        {content.filter(item => item.type === "Book").map(({ title, large_cover_url }, index) => (
                            <Card
                                key={index}
                                title={title}
                                image={large_cover_url}
                            />
                        ))}
                    </Grid>
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
