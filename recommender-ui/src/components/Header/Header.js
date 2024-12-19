import React from 'react';
import { AppBar, Toolbar, Typography, IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Navigation from './Navigation';
import Logo from './Logo';

const Header = () => {
    return (
        <AppBar position="static">
            <Toolbar>
                <IconButton edge="start" color="inherit" aria-label="menu">
                    <MenuIcon />
                </IconButton>
                <Logo />
                <Typography variant="h6" style={{ flexGrow: 1 }}>
                    My Recommender
                </Typography>
                <Navigation />
            </Toolbar>
        </AppBar>
    );
};

export default Header;
