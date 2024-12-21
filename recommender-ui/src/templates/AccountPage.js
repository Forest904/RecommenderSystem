import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Grid, Paper } from '@mui/material';

function AccountPage() {
  const [userData, setUserData] = useState({ username: '', email: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch user details when the component mounts
    const fetchUserData = async () => {
      setLoading(true);
      try {
        const response = await axios.get('/account', { params: { user_id: 1 } }); // Replace with actual user ID logic
        setUserData(response.data);
      } catch (err) {
        setError('Failed to fetch user details.');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserData({ ...userData, [name]: value });
  };

  const handleUpdate = async () => {
    setLoading(true);
    try {
      await axios.put('/account', { user_id: 1, ...userData }); // Replace with actual user ID logic
      alert('Account details updated successfully!');
    } catch (err) {
      setError('Failed to update account details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Grid container spacing={3} justify="center">
        <Grid item xs={12} sm={8} md={6}>
          <Paper style={{ padding: '20px', marginTop: '20px' }}>
            <Typography variant="h4" gutterBottom>
              Account Details
            </Typography>
            {error && (
              <Typography color="error" gutterBottom>
                {error}
              </Typography>
            )}
            <form>
              <TextField
                fullWidth
                margin="normal"
                label="Username"
                name="username"
                value={userData.username}
                onChange={handleInputChange}
                disabled={loading}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Email"
                name="email"
                value={userData.email}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleUpdate}
                disabled={loading}
                style={{ marginTop: '20px' }}
              >
                Update Account
              </Button>
            </form>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default AccountPage;
