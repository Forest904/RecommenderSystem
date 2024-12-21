import React from 'react';
import { Button } from '@mui/material';
import { Link } from 'react-router-dom';

const Navigation = () => {
    return (
        <div>
            <Button color="inherit" component={Link} to="/">
                Home
            </Button>
            <Button color="inherit" component={Link} to="/library">
                Library
            </Button>
            <Button color="inherit" component={Link} to="/account">
                Account
            </Button>
        </div>
    );
};

export default Navigation;
