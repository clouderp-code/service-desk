import React from 'react';
import { Typography, Paper, Box } from '@mui/material';

const HomePage: React.FC = () => {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Welcome to AI Service Desk
      </Typography>
      <Typography paragraph>
        Your intelligent customer support solution powered by AI.
      </Typography>
    </Paper>
  );
};

export default HomePage;
