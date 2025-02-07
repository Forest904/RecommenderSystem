import React from 'react';
import {
  Card as MUICard,
  CardMedia,
  CardContent,
  Typography,
  Button,
  IconButton,
} from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import BookIcon from '@mui/icons-material/Book';
import MovieIcon from '@mui/icons-material/Movie';

const Card = ({
  title,
  image,
  actionLabel,
  onAction,
  userId,
  contentId,
  isLiked,
  onLikeToggle,
  contentType,
}) => {
  // Ensure valid image URL
  const imageUrl =
    image && image.startsWith('http') ? image : '/placeholder-image.jpg';

  const contentIcon =
    contentType === 'book' ? (
      <BookIcon fontSize="small" color="primary" />
    ) : contentType === 'movie' ? (
      <MovieIcon fontSize="small" color="primary" />
    ) : null;

  return (
    <MUICard
      style={{
        margin: '1rem',
        height: '270px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <CardMedia
        component="img"
        image={imageUrl}
        alt={title || 'Placeholder title'}
        style={{
          flex: '1 1 auto',
          width: '100%',
          height: '100%',
          objectFit: 'contain', // ensures the entire image is visible vertically
        }}
        onError={(e) => {
          console.error("Image failed to load:", e.target.src);
          e.target.onerror = null; // Prevents infinite loop if the placeholder fails
          e.target.src = '/placeholder-image.jpg';
        }}
      />
      <CardContent
        style={{
          flex: '0 0 auto',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-end',
          position: 'relative',
        }}
      >
        <Typography
          variant="body2"
          component="div"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            {contentIcon} {title}
          </span>
          {userId ? (
            <IconButton onClick={onLikeToggle} color="primary">
              {isLiked ? <FavoriteIcon color="error" /> : <FavoriteBorderIcon />}
            </IconButton>
          ) : null}
        </Typography>
        {actionLabel && onAction && (
          <Button
            variant="contained"
            color="primary"
            onClick={onAction}
            style={{ marginTop: 'auto' }}
          >
            {actionLabel}
          </Button>
        )}
      </CardContent>
    </MUICard>
  );
};

export default Card;
