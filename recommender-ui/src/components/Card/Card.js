import React from 'react';
import { Card as MUICard, CardMedia, CardContent, Typography, Button } from '@mui/material';

const Card = ({ title, image, type, actionLabel, onAction }) => {
    return (
        <MUICard style={{ margin: '1rem', height: '250px', display: 'flex', flexDirection: 'column' }}>
            <CardMedia
                component="div"
                style={{ flex: '0 0 140px', backgroundSize: 'cover', backgroundPosition: 'center', backgroundImage: `url(${image})` }}
                alt={title || "Placeholder title"}
            />
            <CardContent style={{ flex: '1 1 auto', overflow: 'auto' }}>
                <Typography variant="h7" component="div">
                    {title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    {type}
                </Typography>
                {actionLabel && onAction && (
                    <Button variant="contained" color="primary" onClick={onAction} style={{ marginTop: 'auto' }}>
                        {actionLabel}
                    </Button>
                )}
            </CardContent>
        </MUICard>
    );
};

export default Card;
