import React, { createContext, useState, useMemo } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

export const ThemeContext = createContext();

export function ThemeProviderWrapper({ children }) {
  const [darkMode, setDarkMode] = useState(false);

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? 'dark' : 'light',
          primary: {
            main: darkMode ? '#90caf9' : '#1976d2', // Light Blue in dark mode, Default Blue in light mode
          },
          secondary: {
            main: darkMode ? '#f48fb1' : '#d32f2f', // Pink in dark mode, Red in light mode
          },
          background: {
            default: darkMode ? '#222831' : '#f5f5f5', // Dark Gray for dark mode, Light Gray for light mode
            paper: darkMode ? '#1e1e1e' : '#ffffff', // Darker background for cards
          },
          text: {
            primary: darkMode ? '#ffffff' : '#000000', // White text in dark mode, Black text in light mode
            secondary: darkMode ? '#b0bec5' : '#757575', // Grayish text for secondary elements
          },
        },
      }),
    [darkMode]
  );

  const toggleDarkMode = () => {
    setDarkMode((prevMode) => !prevMode);
  };

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
}
