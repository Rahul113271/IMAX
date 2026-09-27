import { useState, useEffect, useCallback, useRef } from 'react';
import Antigravity from './components/Antigravity/Antigravity';
import SearchBar from './components/SearchBar/SearchBar';
import Carousel from './components/Carousel/Carousel';
import MovieCard from './components/MovieCard/MovieCard';
import MovieModal from './components/MovieModal/MovieModal';
import RotatingText from './components/RotatingText/RotatingText';
import BubbleMenu from './components/BubbleMenu/BubbleMenu';
import './App.css';

const ROTATING_WORDS = ["Favorite", "Action", "Horror", "Romance", "Sci-Fi", "Anime"];

function App() {
  const [carouselItems, setCarouselItems] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [sourceMovie, setSourceMovie] = useState(null);
  const [modalMovie, setModalMovie] = useState(null);
  const [activeIndustry, setActiveIndustry] = useState(null);

  // Mouse tracking for Antigravity background
  const mousePos = useRef({ x: 0, y: 0 });
  const [externalMouse, setExternalMouse] = useState({ x: 0, y: 0 });
  const [clickBurst, setClickBurst] = useState(null);
  const clickIdRef = useRef(0);

  // Track global mouse movement — normalize to -1..1 range
  useEffect(() => {
    let rafId;
    const handleMouseMove = (e) => {
      mousePos.current = {
        x: (e.clientX / window.innerWidth) * 2 - 1,
        y: -(e.clientY / window.innerHeight) * 2 + 1,
      };
    };

    // Throttle state updates via rAF to avoid excessive re-renders
    const tick = () => {
      setExternalMouse({ x: mousePos.current.x, y: mousePos.current.y });
      rafId = requestAnimationFrame(tick);
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    rafId = requestAnimationFrame(tick);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(rafId);
    };
  }, []);

  // Track global mouse clicks — trigger burst effect
  useEffect(() => {
    const handleClick = (e) => {
      clickIdRef.current += 1;
      setClickBurst({
        x: (e.clientX / window.innerWidth) * 2 - 1,
        y: -(e.clientY / window.innerHeight) * 2 + 1,
        id: clickIdRef.current,
      });
    };

    window.addEventListener('click', handleClick);
    return () => window.removeEventListener('click', handleClick);
  }, []);

  // Fetch carousel posters on mount
  useEffect(() => {
    const fetchCarousel = async () => {
      try {
        const res = await fetch('/api/carousel');
        const data = await res.json();
        setCarouselItems(data.items || []);
      } catch (err) {
        console.error('Failed to fetch carousel:', err);
      }
    };
    fetchCarousel();
  }, []);

  // Fetch recommendations when a movie is selected
  const handleMovieSelect = useCallback(async (title) => {
    setSelectedMovie(title);
    setIsLoading(true);
    setError('');
    setRecommendations([]);

    try {
      const res = await fetch(`/api/recommend?movie=${encodeURIComponent(title)}`);
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setRecommendations(data.recommendations || []);
        setSourceMovie(data.source || null);
      }
    } catch (err) {
      setError('Failed to fetch recommendations. Is the API server running?');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch industry movies when filter changes
  useEffect(() => {
    if (activeIndustry) {
      const fetchIndustry = async () => {
        setIsLoading(true);
        setError('');
        try {
          const res = await fetch(`/api/industry?industry=${activeIndustry}`);
          const data = await res.json();
          if (data.error) throw new Error(data.error);
          setRecommendations(data.movies);
          setSelectedMovie(`Top ${activeIndustry} Movies`);
        } catch (err) {
          setError(`Failed to load ${activeIndustry} movies.`);
          console.error(err);
        } finally {
          setIsLoading(false);
        }
      };
      fetchIndustry();
    } else {
      // Clear when industry is deselected
      setRecommendations([]);
      setSelectedMovie('');
    }
  }, [activeIndustry]);

  return (
    <>
      {/* Netflix Background */}
      <div className="netflix-bg" aria-hidden="true">
        <div className="netflix-posters">
          {[...carouselItems, ...carouselItems, ...carouselItems, ...carouselItems, ...carouselItems].map((item, i) => (
            <img key={`bg-${i}`} src={item.poster} alt="" className="netflix-poster" />
          ))}
        </div>
        <div className="netflix-vignette"></div>
        <div className="netflix-curve-container">
          <div className="netflix-curve"></div>
        </div>
      </div>

      {/* Content Overlay */}
      <div className="app-content">
        {/* Header */}
        <header className="header">
          <div className="header-inner">
            <div className="logo">
              <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M15.91 11.672a.375.375 0 010 .656l-5.603 3.113a.375.375 0 01-.557-.328V8.887c0-.286.307-.466.557-.327l5.603 3.112z" fill="currentColor" />
                <circle cx="12" cy="12" r="10" />
              </svg>
              <h1 className="logo-text">
                Cine<span className="logo-accent">Match</span>
              </h1>
            </div>
            <BubbleMenu onSelect={setActiveIndustry} activeIndustry={activeIndustry} />
          </div>
        </header>

        {/* Hero Section & SearchBar (hidden if industry selected) */}
        {!activeIndustry && (
          <section className="hero-section">
            <div className="hero-text">
              <h2 className="hero-title">
                Discover Your Next <RotatingText words={ROTATING_WORDS} interval={1000} /> Movie
              </h2>
              <p className="hero-subtitle">
                Search from thousands of movies and get personalized recommendations powered by machine learning
              </p>
            </div>

            <SearchBar onSelect={handleMovieSelect} industry={activeIndustry} />
          </section>
        )}

        {/* Featured Carousel (hidden if industry selected) */}
        {!activeIndustry && carouselItems.length > 0 && (
          <section className="section carousel-section">
            <h2 className="section-title">
              <span className="section-icon">⭐</span>
              Top Rated Movies
            </h2>
            <Carousel items={carouselItems} />
          </section>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="loading-container">
            <div className="loading-spinner" />
            <p className="loading-text">Finding movies similar to <strong>{selectedMovie}</strong>...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-container">
            <p className="error-text">⚠️ {error}</p>
          </div>
        )}

        {/* Recommendations Grid */}
        {recommendations.length > 0 && (
          <section className="section results-section">
            <h2 className="section-title">
              <span className="section-icon">🎬</span>
              Recommendations for <span className="text-glow">{selectedMovie}</span>
            </h2>
            <p className="section-subtitle">
              {recommendations.length} movies similar to your selection
            </p>
            <div className="movie-grid">
              {recommendations.map((movie, index) => (
                <MovieCard
                  key={index}
                  movie={movie}
                  index={index}
                  onClick={(m) => setModalMovie(m)}
                />
              ))}
            </div>
          </section>
        )}

        {/* Footer */}
        <footer className="footer">
          <p>Powered by TMDB &amp; Cosine Similarity</p>
        </footer>
      </div>

      {/* Movie Detail Modal */}
      {modalMovie && (
        <MovieModal
          movie={modalMovie}
          sourceMovie={sourceMovie}
          onClose={() => setModalMovie(null)}
        />
      )}
    </>
  );
}

export default App;
