import { useState, useEffect, useRef, useCallback } from 'react';
import './Carousel.css';

const Carousel = ({ items = [] }) => {
  const scrollRef = useRef(null);
  const [isPaused, setIsPaused] = useState(false);
  const intervalRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    if (!scrollRef.current || items.length === 0) return;

    const startAutoScroll = () => {
      intervalRef.current = setInterval(() => {
        if (isPaused) return;
        const el = scrollRef.current;
        if (!el) return;

        const maxScroll = el.scrollWidth - el.clientWidth;
        if (el.scrollLeft >= maxScroll - 2) {
          el.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          el.scrollBy({ left: 220, behavior: 'smooth' });
        }
      }, 3000);
    };

    startAutoScroll();
    return () => clearInterval(intervalRef.current);
  }, [items.length, isPaused]);

  const scroll = useCallback((direction) => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollBy({ left: direction * 300, behavior: 'smooth' });
  }, []);

  if (items.length === 0) return null;

  return (
    <div
      className="carousel"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <button
        className="carousel-btn carousel-btn-left"
        onClick={() => scroll(-1)}
        aria-label="Scroll left"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>

      <div className="carousel-track" ref={scrollRef}>
        {items.map((item, i) => {
          const ratingClass =
            item.vote_average >= 8 ? 'high' : item.vote_average >= 6 ? 'mid' : 'low';
          return (
            <div className="carousel-slide" key={i}>
              <div className="carousel-poster-wrap">
                <img
                  src={item.poster}
                  alt={item.title || `Movie ${i + 1}`}
                  className="carousel-poster"
                  loading="lazy"
                />
                <div className="carousel-overlay">
                  {item.vote_average > 0 && (
                    <span className={`carousel-rating rating-${ratingClass}`}>
                      ★ {item.vote_average.toFixed(1)}
                    </span>
                  )}
                  {item.title && <div className="carousel-title">{item.title}</div>}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <button
        className="carousel-btn carousel-btn-right"
        onClick={() => scroll(1)}
        aria-label="Scroll right"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
    </div>
  );
};

export default Carousel;
