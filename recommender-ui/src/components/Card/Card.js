import React from 'react';
import { Card as MUICard, CardMedia, CardContent, Typography, Button } from '@mui/material';

const Card = ({ title, image, type, actionLabel, onAction }) => {
    return (
        <MUICard style={{ margin: '1rem' }}>
            <CardMedia
                component="img"
                height="140"
                image={image}
                alt={title || "Placeholder title"}
            />
            <CardContent>
                <Typography variant="h5" component="div">
                    {title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    {type}
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
