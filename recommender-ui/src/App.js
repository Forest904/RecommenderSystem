import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LibraryPage from './templates/LibraryPage';
import Recommendations from './templates/Recommendations';
import ProfilePage from './templates/ProfilePage';
import LoginPage from './templates/LoginPage';


function App() {
  return (
    <Router>
      <Routes>
      <Route path="/" element={<Recommendations />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/account" element={<ProfilePage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="*" element={<Recommendations />} />
      </Routes>
    </Router>
  );
}

export default App;