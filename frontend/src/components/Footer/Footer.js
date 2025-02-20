import React, { useContext } from "react";
import { Typography, Container, Box } from "@mui/material";
import { ThemeContext } from "../../ThemeContext";

const Footer = () => {
  const { darkMode } = useContext(ThemeContext);

  return (
    <Box
      component="footer"
      py={3}
      mt={5}
      sx={{
        bgcolor: darkMode ? "grey.900" : "grey.200", // Dynamic background color
        color: darkMode ? "grey.300" : "textSecondary", // Adjust text color
        position: "fixed",
        bottom: 0,
        width: "100%",
      }}
    >
      <Container maxWidth="lg" style={{ textAlign: "center" }}>
        <Typography variant="body2">
          &copy; {new Date().getFullYear()} Yo MaMa. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
