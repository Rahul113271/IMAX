import { useState } from 'react';
import './BubbleMenu.css';

const INDUSTRIES = [
  { label: 'kollywood', lang: 'ta' },
  { label: 'tollywood', lang: 'te' },
  { label: 'bollywood', lang: 'hi' },
  { label: 'sandalwood', lang: 'kn' },
  { label: 'mollywood', lang: 'ml' },
  { label: 'Indian Top Grossing', lang: 'all_in' },
];

const BubbleMenu = ({ onSelect, activeIndustry }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);

  const handleSelect = (industry) => {
    onSelect(industry);
    setIsOpen(false);
  };

  return (
    <>
      <button className="bubble-hamburger" onClick={toggleMenu} aria-label="Open Menu">
        <div className="hamburger-icon">
          <span></span>
          <span></span>
        </div>
        {activeIndustry && (
          <span className="bubble-badge">{activeIndustry}</span>
        )}
      </button>

      <div className={`bubble-overlay ${isOpen ? 'open' : ''}`}>
        <div className="bubble-overlay-header">
          <div className="bubble-overlay-logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15.91 11.672a.375.375 0 010 .656l-5.603 3.113a.375.375 0 01-.557-.328V8.887c0-.286.307-.466.557-.327l5.603 3.112z" fill="currentColor" />
              <circle cx="12" cy="12" r="10" />
            </svg>
            <span>CineMatch</span>
          </div>
          
          <button className="bubble-close" onClick={toggleMenu} aria-label="Close Menu">
            <svg viewBox="0 0 24 24" fill="none" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="bubble-cluster">
          {INDUSTRIES.map((item) => (
            <div
              key={item.label}
              className={`bubble-pill ${activeIndustry === item.label ? 'selected' : ''}`}
              onClick={() => handleSelect(item.label)}
            >
              {item.label}
            </div>
          ))}
        </div>

        {activeIndustry && (
          <button className="bubble-clear-filter" onClick={() => { onSelect(null); setIsOpen(false); }}>
            Show All Movies
          </button>
        )}
      </div>
    </>
  );
};

export default BubbleMenu;
