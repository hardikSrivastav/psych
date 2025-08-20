import { useState } from 'react';
import Head from 'next/head';

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
        
        {/* Main Content */}
        <div style={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center', 
          padding: '40px 20px',
          textAlign: 'center'
        }}>
          <h1 style={{ 
            fontSize: '32px', 
            fontWeight: 'normal', 
            color: '#ffffff', 
            marginBottom: '20px',
            fontFamily: 'monospace'
          }}>
            AI PSYCHOLOGIST
          </h1>
          <p style={{ 
            color: '#22c55e', 
            fontSize: '14px', 
            marginBottom: '40px',
            fontFamily: 'monospace'
          }}>
            SCIENTIFICALLY-GROUNDED THERAPEUTIC SUPPORT
          </p>
          
          {/* Status Card */}
          <div style={{ 
            background: '#111111', 
            border: '1px solid #22c55e', 
            borderRadius: '8px',
            padding: '30px',
            maxWidth: '400px',
            width: '100%'
          }}>
            <p style={{ 
              color: '#ffffff', 
              fontSize: '14px', 
              marginBottom: '10px',
              fontFamily: 'monospace'
            }}>
              STATUS: OPERATIONAL
            </p>
            <p style={{ 
              color: '#22c55e', 
              fontSize: '12px', 
              marginBottom: '20px',
              fontFamily: 'monospace'
            }}>
              SESSION ID: {sessionId || 'NONE'}
            </p>
            <div style={{ 
              width: '100%', 
              height: '2px', 
              background: '#22c55e',
              marginTop: '20px'
            }}></div>
          </div>
        </div>
      </main>
    </>
  );
}
