import React, { useContext } from 'react';
import { AppBar, Toolbar, IconButton } from '@mui/material';
import { DarkMode, LightMode } from '@mui/icons-material';
import Navigation from './Navigation';
import Logo from './Logo';
import { ThemeContext } from '../../ThemeContext';

function Header() {
  const { darkMode, toggleDarkMode } = useContext(ThemeContext);

  return (
    <AppBar position="static">
      <Toolbar>
        <Logo />
        <Navigation />
        <IconButton onClick={toggleDarkMode} color="inherit" sx={{ marginLeft: 'auto' }}>
          {darkMode ? <LightMode /> : <DarkMode />}
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
