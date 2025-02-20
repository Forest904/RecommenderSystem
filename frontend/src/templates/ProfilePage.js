import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  Paper,
  Button,
  Avatar,
  IconButton,
  TextField,
  Box
} from '@mui/material';
import { Add, Check } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

function UserProfile() {
  const [userData, setUserData] = useState({
    username: '',
    first_name: '',
    last_name: '',
    date_of_birth: '',
    avatar_url: '',
    bio: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [userColor, setUserColor] = useState('#000000');
  const navigate = useNavigate();
  const colorInputRef = useRef(null);

  const storedUser = localStorage.getItem('user');
  const user = storedUser ? JSON.parse(storedUser) : null;
  const userId = user?.id || '0';

  useEffect(() => {
    if (userId === '0') {
      navigate('/login');
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
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleUpdateProfile = async () => {
    try {
      await axios.post('http://localhost:5000/update_profile', {
        user_id: userId,
        ...userData,
        user_color: userColor
      });
      setEditMode(false);
    } catch (err) {
      setError('Failed to update profile.');
    }
  };

  // Handler to trigger the hidden color input when clicking on the avatar.
  const handleAvatarClick = () => {
    if (colorInputRef.current) {
      colorInputRef.current.click();
    }
  };

  return (
    <>
      <Container>
        <Paper style={{ padding: '20px', marginTop: '20px' }}>
          <Typography variant="h4" gutterBottom>
            User Profile
          </Typography>
          {error && <Typography color="error" gutterBottom>{error}</Typography>}
          {loading ? (
            <Typography>Loading...</Typography>
          ) : (
            <>
              {/* Hidden color input */}
              <input
                type="color"
                ref={colorInputRef}
                value={userColor}
                onChange={(e) => setUserColor(e.target.value)}
                style={{ display: 'none' }}
              />

              {/* Header row with avatar on the left and plus icon on the right */}
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Avatar
                  style={{ backgroundColor: userColor, width: 60, height: 60, cursor: 'pointer' }}
                  src={userData.avatar_url || undefined}
                  onClick={handleAvatarClick}
                />
                <IconButton onClick={() => setEditMode(!editMode)}>
                  <Add />
                </IconButton>
              </Box>

              {/* View Mode: display all non-null fields */}
              {!editMode ? (
                <>
                  {userData.username && (
                    <Typography variant="h6">Username: {userData.username}</Typography>
                  )}
                  {userData.first_name && (
                    <Typography variant="h6">First Name: {userData.first_name}</Typography>
                  )}
                  {userData.last_name && (
                    <Typography variant="h6">Last Name: {userData.last_name}</Typography>
                  )}
                  {userData.date_of_birth && (
                    <Typography variant="h6">Date of Birth: {userData.date_of_birth}</Typography>
                  )}
                  {userData.bio && (
                    <Typography variant="h6">Bio: {userData.bio}</Typography>
                  )}
                </>
              ) : (
                // Edit Mode: provide input fields for profile details except username.
                <>
                  <TextField
                    fullWidth
                    label="First Name"
                    value={userData.first_name || ''}
                    onChange={(e) => setUserData({ ...userData, first_name: e.target.value })}
                    margin="normal"
                  />
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={userData.last_name || ''}
                    onChange={(e) => setUserData({ ...userData, last_name: e.target.value })}
                    margin="normal"
                  />
                  <TextField
                    fullWidth
                    label="Date of Birth"
                    type="date"
                    value={userData.date_of_birth || ''}
                    onChange={(e) => setUserData({ ...userData, date_of_birth: e.target.value })}
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                  />
                  <TextField
                    fullWidth
                    label="Bio"
                    multiline
                    rows={3}
                    value={userData.bio || ''}
                    onChange={(e) => setUserData({ ...userData, bio: e.target.value })}
                    margin="normal"
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    startIcon={<Check />}
                    onClick={handleUpdateProfile}
                    style={{ marginTop: '10px' }}
                  >
                    Confirm
                  </Button>
                </>
              )}
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleLogout}
                sx={{ marginTop: '20px' }}
              >
                Logout
              </Button>
            </>
          )}
        </Paper>
      </Container>
    </>
  );
}

export default UserProfile;
