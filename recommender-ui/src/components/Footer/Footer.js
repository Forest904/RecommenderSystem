// Footer.js
import React from "react";
import { Typography, Container, Box } from "@mui/material";

const Footer = () => {
  return (
    <Box
      component="footer"
      py={3}
      mt={5}
      bgcolor="grey.200"
      style={{ position: "fixed", bottom: 0, width: "100%" }}
    >
      <Container maxWidth="lg" style={{ textAlign: "center" }}>
        <Typography variant="body2" color="textSecondary">
          &copy; {new Date().getFullYear()} Yo MaMa. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
