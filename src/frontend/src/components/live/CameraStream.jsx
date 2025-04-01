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
        tracks.forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div
      className="w-full max-w-md p-1 rounded-xl shadow-xl bg-cover bg-center"
      style={{
        backgroundImage: "url('/assets/background.jpg')",
        backgroundColor: '#000',
      }}
    >
      <div className="rounded-lg overflow-hidden backdrop-blur-sm bg-black/70">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-auto"
        />
      </div>
    </div>
  );
};

export default CameraStream;
