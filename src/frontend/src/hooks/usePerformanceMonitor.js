import { useEffect, useRef } from 'react';

export const usePerformanceMonitor = (componentName) => {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(performance.now());

  useEffect(() => {
    renderCount.current += 1;
    const currentTime = performance.now();
    const timeSinceLastRender = currentTime - lastRenderTime.current;
    
    // Log performance metrics
    console.debug(`[${componentName}] Performance Metrics:`, {
      renderCount: renderCount.current,
      timeSinceLastRender: `${timeSinceLastRender.toFixed(2)}ms`,
      timestamp: new Date().toISOString()
    });

    // Check for poor performance
    if (timeSinceLastRender > 100) {
      console.warn(`[${componentName}] Slow render detected:`, {
        renderTime: timeSinceLastRender
      });
    }

    lastRenderTime.current = currentTime;
  });
}; 