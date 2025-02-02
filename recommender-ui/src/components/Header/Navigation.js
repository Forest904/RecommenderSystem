import React from 'react';
import { Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function Navigation() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('user_id');

  return (
    <Box sx={{ display: 'flex', gap: 2, marginLeft: 'auto' }}>
      {isLoggedIn && (
        <>
          <Button color="inherit" onClick={() => navigate('/account')}>Account</Button>
          <Button color="inherit" onClick={() => navigate('/library')}>Library</Button>
        </>
      )}
      <Button color="inherit" onClick={() => navigate(isLoggedIn ? '/recommendations'  : '/login')}>
        {isLoggedIn ? 'Home' : 'Login'}
      </Button>
    </Box>
  );
}

export default Navigation;
