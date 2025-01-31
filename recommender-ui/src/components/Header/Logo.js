import React from 'react';
import { Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function Logo() {
  const navigate = useNavigate();
  
  return (
    <Typography 
      variant="h6" 
      component="div" 
      sx={{ cursor: 'pointer' }}
      onClick={() => navigate('/')}
    >
      MyApp
    </Typography>
  );
}

export default Logo;
