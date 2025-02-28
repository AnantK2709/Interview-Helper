import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  Tab,
  Tabs
} from '@mui/material';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Mock data - replace with actual API calls later
const mockSessionData = [
  { date: '2023-01-01', confidence: 65, clarity: 70, engagement: 60 },
  { date: '2023-01-05', confidence: 68, clarity: 72, engagement: 63 },
  { date: '2023-01-10', confidence: 72, clarity: 75, engagement: 70 },
  { date: '2023-01-15', confidence: 75, clarity: 78, engagement: 72 },
  { date: '2023-01-20', confidence: 80, clarity: 82, engagement: 78 },
];

const mockFeedbackData = [
  { 
    id: 1, 
    date: '2023-01-20', 
    strengths: ['Clear vocal delivery', 'Strong eye contact', 'Structured answers'],
    improvements: ['Reduce filler words', 'More specific examples', 'Improve posture'],
    overallScore: 78
  },
  { 
    id: 2, 
    date: '2023-01-15', 
    strengths: ['Enthusiastic tone', 'Good pacing', 'Relevant examples'],
    improvements: ['Maintain eye contact', 'Reduce hand gestures', 'More concise answers'],
    overallScore: 72
  },
];

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AnalyticsDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [progressData, setProgressData] = useState(mockSessionData);
  const [feedbackData, setFeedbackData] = useState(mockFeedbackData);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Performance Analytics</Typography>
      
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="analytics tabs">
            <Tab label="Performance Overview" />
            <Tab label="Detailed Feedback" />
            <Tab label="Improvement Areas" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Progress Over Time</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={progressData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="confidence" stroke="#8884d8" />
                    <Line type="monotone" dataKey="clarity" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="engagement" stroke="#ff7300" />
                  </LineChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Latest Session</Typography>
                {progressData.length > 0 && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Session Date: {progressData[progressData.length - 1].date}
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2">Confidence</Typography>
                      <Box sx={{ 
                        width: '100%', 
                        backgroundColor: '#e0e0e0', 
                        borderRadius: 1,
                        mt: 0.5,
                        mb: 1.5
                      }}>
                        <Box sx={{
                          height: 10,
                          borderRadius: 1,
                          backgroundColor: '#8884d8',
                          width: `${progressData[progressData.length - 1].confidence}%`
                        }} />
                      </Box>
                      
                      <Typography variant="subtitle2">Clarity</Typography>
                      <Box sx={{ 
                        width: '100%', 
                        backgroundColor: '#e0e0e0', 
                        borderRadius: 1,
                        mt: 0.5,
                        mb: 1.5
                      }}>
                        <Box sx={{
                          height: 10,
                          borderRadius: 1,
                          backgroundColor: '#82ca9d',
                          width: `${progressData[progressData.length - 1].clarity}%`
                        }} />
                      </Box>
                      
                      <Typography variant="subtitle2">Engagement</Typography>
                      <Box sx={{ 
                        width: '100%', 
                        backgroundColor: '#e0e0e0', 
                        borderRadius: 1,
                        mt: 0.5
                      }}>
                        <Box sx={{
                          height: 10,
                          borderRadius: 1,
                          backgroundColor: '#ff7300',
                          width: `${progressData[progressData.length - 1].engagement}%`
                        }} />
                      </Box>
                    </Box>
                  </Box>
                )}
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            {feedbackData.map((feedback) => (
              <Grid item xs={12} key={feedback.id}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6">
                    Session on {feedback.date} - Overall Score: {feedback.overallScore}/100
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>Strengths</Typography>
                      <List dense>
                        {feedback.strengths.map((strength, index) => (
                          <ListItem key={index}>
                            <ListItemText primary={strength} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" gutterBottom>Areas for Improvement</Typography>
                      <List dense>
                        {feedback.improvements.map((improvement, index) => (
                          <ListItem key={index}>
                            <ListItemText primary={improvement} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Top Improvement Areas</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={[
                      { name: 'Filler Words', count: 28 },
                      { name: 'Eye Contact', count: 24 },
                      { name: 'Posture', count: 19 },
                      { name: 'Vocal Clarity', count: 15 },
                      { name: 'Answer Structure', count: 12 }
                    ]}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Recommended Exercises</Typography>
                <List>
                  <ListItem>
                    <ListItemText 
                      primary="Filler Word Elimination" 
                      secondary="Practice speaking slowly and deliberately, pausing instead of using filler words."
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Eye Contact Drill" 
                      secondary="Practice maintaining eye contact with an object while speaking for 30 seconds at a time."
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Posture Improvement" 
                      secondary="Practice sitting and standing straight with shoulders back for 10 minutes daily."
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Vocal Clarity Exercises" 
                      secondary="Practice enunciation exercises using tongue twisters daily."
                    />
                  </ListItem>
                </List>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
      </Box>
    </Box>
  );
};

export default AnalyticsDashboard;