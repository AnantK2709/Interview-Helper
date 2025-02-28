// src/components/WebcamTest.tsx
import React, { useRef, useState } from 'react';
import Webcam from 'react-webcam';

const WebcamTest: React.FC = () => {
  const webcamRef = useRef<Webcam>(null);
  const [isCapturing, setIsCapturing] = useState(false);

  const startCapture = () => {
    setIsCapturing(true);
  };

  const stopCapture = () => {
    setIsCapturing(false);
  };

  return (
    <div>
      <h2>Webcam Test</h2>
      <div>
        <Webcam
          audio={true}
          ref={webcamRef}
          width={640}
          height={480}
          videoConstraints={{
            width: 640,
            height: 480,
            facingMode: 'user',
          }}
        />
      </div>
      <div>
        {!isCapturing ? (
          <button onClick={startCapture}>Start Capture</button>
        ) : (
          <button onClick={stopCapture}>Stop Capture</button>
        )}
      </div>
    </div>
  );
};

export default WebcamTest;