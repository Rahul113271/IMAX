import { useState, useEffect } from 'react';
import './RotatingText.css';

const RotatingText = ({ words, interval = 2500 }) => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % words.length);
    }, interval);
    return () => clearInterval(timer);
  }, [words, interval]);

  return (
    <span className="rotating-text-wrapper highlight">
      {words.map((word, i) => {
        let className = 'rotating-text-item';
        if (i === index) {
          className += ' active';
        } else if (i === (index - 1 + words.length) % words.length) {
          className += ' exiting';
        }

        return (
          <span key={word} className={className}>
            {word}
          </span>
        );
      })}
    </span>
  );
};

export default RotatingText;
