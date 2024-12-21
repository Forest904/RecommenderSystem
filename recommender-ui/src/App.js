import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AccountPage from './templates/AccountPage';
import LibraryPage from './templates/LibraryPage';
import Recommendations from './templates/Recommendations';

function App() {
  return (
    <Router>
      <Routes>
      <Route path="/" element={<Recommendations />} />
        <Route path="/account" element={<AccountPage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="*" element={<Recommendations />} />
      </Routes>
    </Router>
  );
}

export default App;