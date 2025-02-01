import React from 'react';
import { Card as MUICard, CardMedia, CardContent, Typography, Button } from '@mui/material';

const Card = ({ title, image, actionLabel, onAction }) => {
    return (
        <MUICard
  style={{
    margin: '1rem',
    height: '250px',
    display: 'flex',
    flexDirection: 'column',
  }}
>
  <CardMedia
    component="div"
    // Allow the image to grow and fill the remaining space
    style={{
      flex: '1 1 auto',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundImage: `url(${image})`,
    }}
    alt={title || "Placeholder title"}
  />
  <CardContent
    // Keep the content at its intrinsic height
    style={{
      flex: '0 0 auto',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-end', // push content to the bottom
    }}
  >
    <Typography variant="body2" component="div">
      {title}
    </Typography>
    {actionLabel && onAction && (
      <Button
        variant="contained"
        color="primary"
        onClick={onAction}
        style={{ marginTop: 'auto' }} // if you want to push the button to the bottom as well
      >
        {actionLabel}
      </Button>
    )}
  </CardContent>
</MUICard>

    );
};

export default Card;
