import { useState, useEffect, useRef, useCallback } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSelect, industry }) => {
  const [query, setQuery] = useState('');
  const [allMovies, setAllMovies] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(true);
  const inputRef = useRef(null);
  const listRef = useRef(null);
  const containerRef = useRef(null);

  // Fetch movie titles (re-fetches when industry filter changes)
  useEffect(() => {
    const fetchMovies = async () => {
      setIsLoading(true);
      try {
        const url = industry
          ? `/api/movies?industry=${encodeURIComponent(industry)}`
          : '/api/movies';
        const res = await fetch(url);
        const data = await res.json();
        setAllMovies(data.movies || []);
      } catch (err) {
        console.error('Failed to fetch movies:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchMovies();
    // Clear search when industry changes
    setQuery('');
    setSuggestions([]);
    setIsOpen(false);
  }, [industry]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = useCallback(
    (e) => {
      const value = e.target.value;
      setQuery(value);
      setActiveIndex(-1);

      if (value.trim().length < 1) {
        setSuggestions([]);
        setIsOpen(false);
        return;
      }

      const lower = value.toLowerCase();
      const filtered = allMovies
        .filter((m) => m.toLowerCase().includes(lower))
        .slice(0, 12);
      setSuggestions(filtered);
      setIsOpen(filtered.length > 0);
    },
    [allMovies]
  );

  const selectMovie = useCallback(
    (title) => {
      setQuery(title);
      setIsOpen(false);
      setSuggestions([]);
      setActiveIndex(-1);
      onSelect(title);
    },
    [onSelect]
  );

  const handleKeyDown = useCallback(
    (e) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setActiveIndex((prev) =>
            prev < suggestions.length - 1 ? prev + 1 : 0
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setActiveIndex((prev) =>
            prev > 0 ? prev - 1 : suggestions.length - 1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (activeIndex >= 0 && suggestions[activeIndex]) {
            selectMovie(suggestions[activeIndex]);
          }
          break;
        case 'Escape':
          setIsOpen(false);
          setActiveIndex(-1);
          break;
      }
    },
    [isOpen, activeIndex, suggestions, selectMovie]
  );

  // Scroll active item into view
  useEffect(() => {
    if (activeIndex >= 0 && listRef.current) {
      const item = listRef.current.children[activeIndex];
      if (item) {
        item.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [activeIndex]);

  return (
    <div className="search-bar" ref={containerRef}>
      <div className="search-input-wrapper">
        <svg
          className="search-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <input
          ref={inputRef}
          id="movie-search"
          type="text"
          className="search-input"
          placeholder={isLoading ? 'Loading movies...' : 'Search for a movie...'}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (suggestions.length > 0) setIsOpen(true);
          }}
          disabled={isLoading}
          autoComplete="off"
          aria-label="Search movies"
          aria-autocomplete="list"
          aria-expanded={isOpen}
          aria-controls="search-suggestions"
        />
        {query && (
          <button
            className="search-clear"
            onClick={() => {
              setQuery('');
              setSuggestions([]);
              setIsOpen(false);
              inputRef.current?.focus();
            }}
            aria-label="Clear search"
          >
            ✕
          </button>
        )}
      </div>

      {isOpen && suggestions.length > 0 && (
        <ul
          ref={listRef}
          id="search-suggestions"
          className="search-dropdown"
          role="listbox"
        >
          {suggestions.map((title, index) => (
            <li
              key={title}
              className={`search-option ${index === activeIndex ? 'active' : ''}`}
              role="option"
              aria-selected={index === activeIndex}
              onMouseEnter={() => setActiveIndex(index)}
              onClick={() => selectMovie(title)}
            >
              <svg
                className="option-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
              >
                <path d="M7 4v16l13-8z" />
              </svg>
              <span className="option-text">{title}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchBar;
