import React from 'react';
import { Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function Navigation() {
  const navigate = useNavigate();
  const storedUser = localStorage.getItem('user');
  const user = storedUser ? JSON.parse(storedUser) : null;
  const isLoggedIn = !!user?.id;

  return (
    <Box sx={{ display: 'flex', gap: 2, marginLeft: 'auto' }}>
      {isLoggedIn && (
        <>
          <Button color="inherit" onClick={() => navigate('/showcase')}>Showcase</Button>
          <Button color="inherit" onClick={() => navigate('/favorites')}>Favorites</Button>
          <Button color="inherit" onClick={() => navigate('/foryou')}>For You</Button>
        </>
      )}
      {!isLoggedIn && (
        <>
          <Button color="inherit" onClick={() => navigate('/showcase')}>Showcase</Button>
        </>
      )}
      <Button color="inherit" onClick={() => navigate(isLoggedIn ? '/account' : '/login')}>
        {isLoggedIn ? 'Account' : 'Login'}
      </Button>
    </Box>
  );
}

export default Navigation;
