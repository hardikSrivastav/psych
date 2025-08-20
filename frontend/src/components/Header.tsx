import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">🧠</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">AI Psychologist</h1>
              <p className="text-white/70 text-sm">Scientifically-grounded therapeutic support</p>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-4 text-white/70 text-sm">
            <span>🔒 Private & Secure</span>
            <span>⚡ Real-time</span>
            <span>📚 Research-based</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
