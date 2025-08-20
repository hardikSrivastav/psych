import { useState } from 'react';
import Head from 'next/head';
import ChatInterface from '../components/ChatInterface';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);

  return (
    <>
      <Head>
        <title>AI Psychologist</title>
        <meta name="description" content="Scientifically-grounded therapeutic conversations" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#000000' }}>
        {/* Minimal Header */}
        <header style={{ 
          background: '#000000',
          borderBottom: '1px solid #22c55e',
          padding: '20px'
        }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{ fontSize: '18px', fontWeight: 'normal', color: '#ffffff', margin: 0, fontFamily: 'monospace' }}>AI PSYCHOLOGIST</h1>
              <p style={{ color: '#22c55e', fontSize: '12px', margin: '4px 0 0 0', fontFamily: 'monospace' }}>THERAPEUTIC CONVERSATIONS</p>
            </div>
            <div style={{ display: 'flex', gap: '20px', fontSize: '12px', color: '#666666', fontFamily: 'monospace' }}>
              <span>PRIVATE</span>
              <span>SECURE</span>
              <span>RESEARCH-BASED</span>
            </div>
          </div>
        </header>
        
        {/* Chat Interface */}
        <div style={{ flex: 1 }}>
          <ChatInterface sessionId={sessionId} setSessionId={setSessionId} />
        </div>
      </main>
    </>
  );
}
