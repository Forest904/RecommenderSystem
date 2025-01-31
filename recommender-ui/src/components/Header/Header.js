import React from 'react';
import { AppBar, Toolbar } from '@mui/material';
import Navigation from './Navigation';
import Logo from './Logo';

function Header() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Logo />
        <Navigation />
      </Toolbar>
    </AppBar>
  );
}

export default Header;
