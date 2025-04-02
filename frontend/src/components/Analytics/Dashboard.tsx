import React from 'react';
import { Box } from '@mui/material';
import Charts from './Charts';
import Stats from './Stats';

const Dashboard: React.FC = () => {
  return (
    <Box>
      <Stats />
      <Charts />
    </Box>
  );
};

export default Dashboard;
