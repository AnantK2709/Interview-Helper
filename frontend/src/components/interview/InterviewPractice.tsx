import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Box, Button, Typography, Paper, Grid, CircularProgress } from '@mui/material';

const InterviewPractice: React.FC = () => {
  const webcamRef = useRef<Webcam>(null);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<string>("");
  const [feedback, setFeedback] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(3);
  const [showCountdown, setShowCountdown] = useState(false);

  // WebSocket connection for real-time communication
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Fetch a random question when component mounts
    fetchQuestion();

    // Initialize WebSocket connection
    const userId = "user-" + Math.floor(Math.random() * 1000000); // Replace with actual user ID
    socketRef.current = new WebSocket(`ws://localhost:8000/ws/${userId}`);
    
    socketRef.current.onopen = () => {
      console.log('WebSocket connection established');
    };
    
    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received data:', data);
      
      if (data.feedback) {
        setFeedback(data.feedback);
      }
    };
    
    socketRef.current.onclose = () => {
      console.log('WebSocket connection closed');
    };
    
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const fetchQuestion = async () => {
    try {
      const response = await fetch('http://localhost:8000/questions?count=1');
      const data = await response.json();
      if (data && data.length > 0) {
        setCurrentQuestion(data[0].question);
      }
    } catch (error) {
      console.error('Error fetching question:', error);
    }
  };

  const startSession = () => {
    setShowCountdown(true);
    
    // Start countdown
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev === 1) {
          clearInterval(timer);
          setShowCountdown(false);
          setIsSessionActive(true);
          captureFrames();
          return 3;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const stopSession = () => {
    setIsSessionActive(false);
    setFeedback(null);
  };

  const captureFrames = () => {
    if (!isSessionActive) return;
    
    const captureInterval = setInterval(() => {
      if (!isSessionActive || !webcamRef.current) {
        clearInterval(captureInterval);
        return;
      }
      
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc && socketRef.current) {
        // Send frame to backend for processing
        socketRef.current.send(JSON.stringify({
          type: 'frame',
          data: imageSrc
        }));
      }
    }, 1000); // Capture every second
  };

  const nextQuestion = () => {
    setLoading(true);
    fetchQuestion();
    setFeedback(null);
    setLoading(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Interview Practice Session</Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, position: 'relative' }}>
            {showCountdown && (
              <Box sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(0,0,0,0.7)',
                zIndex: 10,
                borderRadius: 1
              }}>
                <Typography variant="h1" color="white">{countdown}</Typography>
              </Box>
            )}
            <Webcam
              audio={true}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              width="100%"
              height="auto"
              videoConstraints={{
                width: 1280,
                height: 720,
                facingMode: "user"
              }}
            />
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              {!isSessionActive ? (
                <Button 
                  variant="contained" 
                  color="primary" 
                  onClick={startSession}
                  fullWidth
                >
                  Start Session
                </Button>
              ) : (
                <Button 
                  variant="contained" 
                  color="error" 
                  onClick={stopSession}
                  fullWidth
                >
                  End Session
                </Button>
              )}
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 2, height: 'calc(50% - 16px)' }}>
            <Typography variant="h6" gutterBottom>Current Question</Typography>
            {loading ? (
              <CircularProgress size={20} sx={{ ml: 2 }} />
            ) : (
              <>
                <Typography variant="body1" paragraph>{currentQuestion}</Typography>
                <Button 
                  variant="outlined" 
                  onClick={nextQuestion}
                  disabled={!isSessionActive}
                >
                  Next Question
                </Button>
              </>
            )}
          </Paper>
          
          <Paper sx={{ p: 2, height: 'calc(50% - 16px)', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>Real-time Feedback</Typography>
            {isSessionActive ? (
              feedback ? (
                <Box>
                  {feedback.facialExpression && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">Facial Expression:</Typography>
                      <Typography variant="body2">
                        {`${feedback.facialExpression.dominant} (${Math.round(feedback.facialExpression.confidence * 100)}% confidence)`}
                      </Typography>
                    </Box>
                  )}
                  
                  {feedback.speechAnalysis && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">Speech Analysis:</Typography>
                      <Typography variant="body2">
                        {`Pace: ${feedback.speechAnalysis.pace} words/min`}
                      </Typography>
                      <Typography variant="body2">
                        {`Filler words: ${feedback.speechAnalysis.fillerWords}`}
                      </Typography>
                    </Box>
                  )}
                  
                  {feedback.posture && (
                    <Box>
                      <Typography variant="subtitle2">Posture:</Typography>
                      <Typography variant="body2">
                        {feedback.posture.status}
                      </Typography>
                    </Box>
                  )}
                </Box>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CircularProgress size={16} sx={{ mr: 1 }} />
                  <Typography variant="body2">Analyzing your performance...</Typography>
                </Box>
              )
            ) : (
              <Typography variant="body2" color="text.secondary">
                Start a session to receive real-time feedback on your interview performance.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default InterviewPractice;