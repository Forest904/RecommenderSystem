import React from 'react';
import { Card as MUICard, CardMedia, CardContent, Typography, Button } from '@mui/material';

const Card = ({ title, image, genre, actionLabel, onAction }) => {
    return (
        <MUICard style={{ margin: '1rem' }}>
            <CardMedia
                component="img"
                height="140"
                image={image || "/public/logo512.png"}
                alt={title || "Placeholder title"}
            />
            <CardContent>
                <Typography variant="h5" component="div">
                    {title}
                </Typography>
                <Typography variant="h3" component="div">
                    {genre}
                </Typography>
                {actionLabel && onAction && (
                    <Button variant="contained" color="primary" onClick={onAction}>
                        {actionLabel}
                    </Button>
                )}
            </CardContent>
        </MUICard>
    );
};

export default Card;
