import { useEffect, useRef } from 'react';

const CameraStream = () => {
  const videoRef = useRef(null);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error('Error accessing camera:', err);
      }
    };

    startCamera();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      className="rounded-xl shadow-xl object-cover"
      style={{
        width: '100%',
        maxWidth: '900px',
        aspectRatio: '4 / 3',
        backgroundColor: 'transparent',
        border: 'none',
      }}
    />
  );
};

export default CameraStream;
