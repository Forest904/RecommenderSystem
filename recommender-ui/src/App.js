import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LibraryPage from './templates/LibraryPage';
import ProfilePage from './templates/ProfilePage';
import LoginPage from './templates/LoginPage';
import ShowcasePage from './templates/ShowcasePage';
import FavoritesPage from './templates/FavoritesPage';
import ForYouPage from './templates/ForYouPage';
import Header from './components/Header/Header';
import { ThemeProviderWrapper } from './ThemeContext';
import Footer from './components/Footer/Footer';

function App() {
  return (
    <ThemeProviderWrapper>
      <Router>
        <Header />
        <Routes>
          <Route path="/" element={<ShowcasePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/account" element={<ProfilePage />} />
          <Route path="/showcase" element={<ShowcasePage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/foryou" element={<ForYouPage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="*" element={<ShowcasePage />} />
        </Routes>
        <Footer />
      </Router>
    </ThemeProviderWrapper>
  );
}

export default App;
