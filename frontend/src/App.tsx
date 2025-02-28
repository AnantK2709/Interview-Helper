import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  CssBaseline,
  Divider,
  IconButton
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  VideoCall as VideoCallIcon,
  History as HistoryIcon,
  AccountCircle as AccountCircleIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import InterviewPractice from './components/interview/InterviewPractice';
import AnalyticsDashboard from './components/dashboard/AnalyticsDashboard';
import './App.css';

// Placeholder components for routes we haven't implemented yet
const SessionHistory = () => <Box p={3}><Typography variant="h4">Session History</Typography></Box>;
const Profile = () => <Box p={3}><Typography variant="h4">User Profile</Typography></Box>;
const Settings = () => <Box p={3}><Typography variant="h4">Settings</Typography></Box>;

function App() {
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  const drawerWidth = 240;
  
  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Practice Interview', icon: <VideoCallIcon />, path: '/practice' },
    { text: 'Session History', icon: <HistoryIcon />, path: '/history' },
    { text: 'Profile', icon: <AccountCircleIcon />, path: '/profile' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' }
  ];

  return (
    <Router>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={toggleDrawer}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              Interview Practice App
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={toggleDrawer}
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              {menuItems.map((item) => (
                <ListItem 
                  button 
                  key={item.text} 
                  component={Link} 
                  to={item.path}
                  onClick={toggleDrawer}
                >
                  <ListItemIcon>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>
        
        <Box component="main" sx={{ flexGrow: 1, p: 0 }}>
          <Toolbar />
          <Container maxWidth="xl" sx={{ mt: 2 }}>
            <Routes>
              <Route path="/" element={<AnalyticsDashboard />} />
              <Route path="/practice" element={<InterviewPractice />} />
              <Route path="/history" element={<SessionHistory />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Container>
        </Box>
      </Box>
    </Router>
  );
}

export default App;