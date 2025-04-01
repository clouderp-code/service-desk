#!/bin/bash

# Base directories
mkdir -p ./{frontend,backend,docs,scripts,tests}

# Backend structure
cd ./backend
mkdir -p {app/{api,core,models,services,utils},tests/{unit,integration}}
mkdir -p app/api/{endpoints,routes,middleware}
mkdir -p app/core/{config,security}
mkdir -p app/services/{agent,chat,knowledge_base,memory}

# Create Python files in backend
touch app/__init__.py
touch app/main.py
touch app/api/__init__.py
touch app/api/endpoints/__init__.py
touch app/api/endpoints/{chat,knowledge_base,analytics}.py
touch app/core/__init__.py
touch app/core/config/{settings,logging}.py
touch app/core/security/{auth,jwt}.py
touch app/models/__init__.py
touch app/models/{chat,knowledge_base,user}.py
touch app/services/__init__.py
touch app/services/agent/{base,tools,memory}.py
touch app/services/chat/{service,websocket}.py
touch app/services/knowledge_base/{service,embeddings}.py
touch app/services/memory/{conversation,vector_store}.py
touch app/utils/{logger,exceptions}.py

# Create backend configuration files
touch {requirements.txt,Dockerfile,.env.example,.gitignore}

# Frontend structure
cd ../frontend
mkdir -p {public,src/{components,pages,services,utils,hooks,styles}}
mkdir -p src/components/{Chat,Layout,KnowledgeBase,Analytics}

# Create frontend files
touch src/index.tsx
touch src/App.tsx
touch src/components/Chat/{ChatWindow,MessageList,InputBox}.tsx
touch src/components/Layout/{Header,Sidebar,Footer}.tsx
touch src/components/KnowledgeBase/{ArticleList,ArticleDetail,Search}.tsx
touch src/components/Analytics/{Dashboard,Charts,Stats}.tsx
touch src/pages/{HomePage,ChatPage,KnowledgeBasePage,AnalyticsPage}.tsx
touch src/services/{api,websocket}.ts
touch src/utils/{types,helpers}.ts
touch src/hooks/{useChat,useWebSocket,useAuth}.ts
touch src/styles/{global,theme}.css

# Create frontend configuration files
touch {package.json,tsconfig.json,.env.example,Dockerfile,.gitignore}

# Create documentation
cd ../docs
touch {README.md,API.md,SETUP.md,ARCHITECTURE.md}

# Create Docker compose and other configuration files
cd ..
touch {docker-compose.yml,.env.example,.gitignore}

echo "Project structure created successfully!" 