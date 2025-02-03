import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, Paper, Grid, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';

function UserProfile() {
  const [userData, setUserData] = useState({ username: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const storedUser = localStorage.getItem('user');
  const user = storedUser ? JSON.parse(storedUser) : null;
  const userId = user?.id || '0';

  useEffect(() => {
    if (userId === '0') {
      navigate('/login'); // Redirect to login page if not logged in
      return;
    }

    const fetchUserData = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`http://localhost:5000/account`, { params: { user_id: userId } });
        setUserData(response.data);
      } catch (err) {
        setError('Failed to fetch user details.');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [userId, navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user'); // Remove user session
    navigate('/login'); // Redirect to login page
  };

  return (
    <>
      <Header title="User Profile" />
      <Container>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} sm={8} md={6}>
            <Paper style={{ padding: '20px', marginTop: '20px' }}>
              <Typography variant="h4" gutterBottom>
                User Profile
              </Typography>
              {error && (
                <Typography color="error" gutterBottom>
                  {error}
                </Typography>
              )}
              {loading ? (
                <Typography>Loading...</Typography>
              ) : (
                <>
                  <Typography variant="h6">Username:</Typography>
                  <Typography>{userData.username}</Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={handleLogout}
                    sx={{
                      backgroundColor: '#fd1b1b',
                      '&:hover': { backgroundColor: '#d11717' },
                      marginTop: '20px'
                    }}
                  >
                    Logout
                  </Button>
                </>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>
      <Footer />
    </>
  );
}

export default UserProfile;
