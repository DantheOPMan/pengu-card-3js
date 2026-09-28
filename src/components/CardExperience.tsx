'use client';

import { useEffect, useRef, useState } from 'react';
import { defaultSettings, type CardScene } from '@/scene/createCardScene';

export default function CardExperience() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<CardScene | null>(null);
  const [autoRotate, setAutoRotate] = useState(false);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    let engine: CardScene | undefined;
    const canvas = canvasRef.current!;
    const fail = (message: string) => {
      if (mounted) { setError(message); setStatus('error'); }
    };
    const contextError = (event: Event) => fail((event as CustomEvent<string>).detail);
    canvas.addEventListener('carderror', contextError);
    void import('@/scene/createCardScene').then(({ createCardScene }) => {
      if (!mounted) return;
      engine = createCardScene(canvas);
      engineRef.current = engine;
      return engine.ready.then(() => { if (mounted) setStatus('ready'); });
    }).catch(() => fail('The card could not load. Please reload with hardware acceleration enabled.'));
    return () => {
      mounted = false;
      canvas.removeEventListener('carderror', contextError);
      engine?.dispose();
      engineRef.current = null;
    };
  }, []);

  useEffect(() => {
    engineRef.current?.update({ ...defaultSettings, autoRotate });
  }, [autoRotate, status]);

  return <main className="exhibition">
    <header className="exhibition-title"><h1>Winter Crown</h1></header>
    <section className={`card-stage ${status === 'ready' ? 'is-ready' : ''}`} aria-label="The Frost King collectible card">
      <canvas
        ref={canvasRef}
        className="webgl-canvas"
        tabIndex={0}
        role="img"
        aria-label="Interactive Winter Crown card. Drag to see either side, or use the left and right arrow keys. Home resets rotation."
        aria-describedby="card-hint"
      />
      {status === 'loading' && <p className="loading-state" role="status">Loading card</p>}
      {status === 'error' && <div className="error-state" role="alert">
        <img src="/assets/penguin-original.png" alt="The Frost King penguin" />
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Reload</button>
      </div>}
    </section>
    <footer className="exhibition-footer">
      <p id="card-hint">Drag to turn</p>
      <button
        className="orbit-button"
        onClick={() => setAutoRotate(value => !value)}
        aria-pressed={autoRotate}
        disabled={status !== 'ready'}
      >
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          {autoRotate
            ? <path d="M5 3v10M11 3v10" stroke="currentColor" strokeWidth="1.5" />
            : <path d="m5 3 8 5-8 5V3Z" stroke="currentColor" strokeLinejoin="round" />}
        </svg>
        <span>Auto orbit</span>
      </button>
    </footer>
  </main>;
}
