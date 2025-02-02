import React, { useState } from 'react';
import axios from 'axios';
import { Container, TextField, Button, Typography, Paper, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header/Header';
import Footer from '../components/Footer/Footer';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();

  const handleAuth = async () => {
    setError('');
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required.');
      return;
    }
  
    try {
      if (isLogin) {
        const response = await axios.post('http://localhost:5000/account', { username, password });
        if (response.data && response.data.user_id) {
          const userData = { id: response.data.user_id, username: response.data.username };
          localStorage.setItem('user', JSON.stringify(userData));
          console.log("User stored in localStorage:", userData);
          navigate('/profile');
        } else {
          setError('Invalid username or password.');
        }
      } else {
        const response = await axios.post('http://localhost:5000/create_user', { username, password });
        if (response.data.message) {
          alert('User created successfully! You can now log in.');
          setIsLogin(true);
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed. Please try again.');
    }
  };

  return (
    <>
      <Header title={isLogin ? 'Login' : 'Create Account'} />
      <Container>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} sm={8} md={6}>
            <Paper style={{ padding: '20px', marginTop: '20px' }}>
              <Typography variant="h4" gutterBottom>
                {isLogin ? 'Login to Your Account' : 'Create a New Account'}
              </Typography>
              {error && (
                <Typography color="error" gutterBottom>
                  {error}
                </Typography>
              )}
              <TextField
                fullWidth
                margin="normal"
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleAuth}
                style={{ marginTop: '20px' }}
              >
                {isLogin ? 'Login' : 'Create Account'}
              </Button>
              <Button
                color="secondary"
                fullWidth
                onClick={() => setIsLogin(!isLogin)}
                style={{ marginTop: '10px' }}
              >
                {isLogin ? 'Need an account? Sign up' : 'Already have an account? Log in'}
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Container>
      <Footer />
    </>
  );
}

export default LoginPage;
