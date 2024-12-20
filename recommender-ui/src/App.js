import React from "react";
import { Container } from "@mui/material";
import Header from './components/Header/Header';
import Footer from './components/Footer/Footer';
import { Users } from './components/Users/Users';
import { Recommendations } from './components/Recommendations/Recommendations';

const App = () => {
  return (
    <>
      {/* Header */}
      <Header />

      <Container>
        {/* Recommendations Module */}
        <Recommendations />

        {/* User Module */}
        <Users />
      </Container>

      {/* Footer */}
      <Footer />
    </>
  );
};

export default App;