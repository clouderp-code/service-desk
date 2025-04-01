import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';

const Header: React.FC = () => {
  return (
    <AppBar position="fixed">
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          AI Service Desk
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
