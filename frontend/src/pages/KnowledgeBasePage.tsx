import React from 'react';
import { Box } from '@mui/material';
import ArticleList from '../components/KnowledgeBase/ArticleList';
import Search from '../components/KnowledgeBase/Search';

const KnowledgeBasePage: React.FC = () => {
  return (
    <Box>
      <Search />
      <ArticleList />
    </Box>
  );
};

export default KnowledgeBasePage;
