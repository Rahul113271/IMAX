import { useState, useEffect, useCallback } from 'react';
import './MovieModal.css';

const MovieModal = ({ movie, sourceMovie, onClose }) => {
  const [detail, setDetail] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  // Fetch additional details (cast, director, backdrop) on open
  useEffect(() => {
    if (!movie?.movie_id) return;

    const fetchDetail = async () => {
      setIsLoadingDetail(true);
      try {
        const res = await fetch(`/api/movie-detail?id=${movie.movie_id}`);
        const data = await res.json();
        setDetail(data);
      } catch (err) {
        console.error('Failed to fetch movie detail:', err);
      } finally {
        setIsLoadingDetail(false);
      }
    };
    fetchDetail();
  }, [movie?.movie_id]);

  // Close on Escape key
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKey);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  // Close on backdrop click
  const handleBackdropClick = useCallback(
    (e) => {
      if (e.target === e.currentTarget) onClose();
    },
    [onClose]
  );

  if (!movie) return null;

  const {
    title,
    poster,
    overview,
    vote_average = 0,
    release_date = '',
    genres = [],
    similarity = 0,
    shared_genres = [],
    tagline = '',
    runtime = 0,
  } = movie;

  const year = release_date ? new Date(release_date).getFullYear() : '';
  const ratingClass =
    vote_average >= 7 ? 'high' : vote_average >= 5 ? 'mid' : 'low';

  const hours = runtime ? Math.floor(runtime / 60) : 0;
  const mins = runtime ? runtime % 60 : 0;
  const runtimeStr = runtime ? `${hours}h ${mins}m` : '';

  // Build recommendation reason
  const buildReasonText = () => {
    const reasons = [];

    if (similarity >= 80) {
      reasons.push(`extremely high content similarity (${similarity}%) with "${sourceMovie?.title}"`);
    } else if (similarity >= 50) {
      reasons.push(`strong content similarity (${similarity}%) with "${sourceMovie?.title}"`);
    } else if (similarity >= 30) {
      reasons.push(`notable content similarity (${similarity}%) with "${sourceMovie?.title}"`);
    } else {
      reasons.push(`content similarity of ${similarity}% with "${sourceMovie?.title}"`);
    }

    if (shared_genres.length > 0) {
      reasons.push(
        `they share ${shared_genres.length === 1 ? 'the genre' : 'genres'}: ${shared_genres.join(', ')}`
      );
    }

    return reasons;
  };

  const reasons = buildReasonText();

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-container" role="dialog" aria-modal="true" aria-label={`Details for ${title}`}>
        {/* Close button */}
        <button className="modal-close" onClick={onClose} aria-label="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>

        {/* Backdrop image */}
        {detail?.backdrop && (
          <div className="modal-backdrop-img" style={{ backgroundImage: `url(${detail.backdrop})` }} />
        )}

        <div className="modal-content">
          {/* Top section: poster + info */}
          <div className="modal-top">
            <div className="modal-poster-wrap">
              <img src={poster} alt={`${title} poster`} className="modal-poster" />
            </div>

            <div className="modal-info">
              <h2 className="modal-title">{title}</h2>
              {tagline && <p className="modal-tagline">"{tagline}"</p>}

              <div className="modal-meta">
                <span className={`modal-rating rating-${ratingClass}`}>
                  ★ {vote_average.toFixed(1)}
                </span>
                {year && <span className="modal-year">{year}</span>}
                {runtimeStr && <span className="modal-runtime">🕐 {runtimeStr}</span>}
              </div>

              {genres.length > 0 && (
                <div className="modal-genres">
                  {genres.map((g) => (
                    <span
                      key={g}
                      className={`modal-genre-tag ${shared_genres.includes(g) ? 'shared' : ''}`}
                    >
                      {g}
                      {shared_genres.includes(g) && <span className="shared-badge">shared</span>}
                    </span>
                  ))}
                </div>
              )}

              {/* Director */}
              {detail?.director && (
                <p className="modal-director">
                  <span className="detail-label">Directed by</span> {detail.director}
                </p>
              )}
            </div>
          </div>

          {/* Plot / Description */}
          <div className="modal-section">
            <h3 className="modal-section-title">📖 Plot</h3>
            <p className="modal-overview">
              {overview || 'No plot information available.'}
            </p>
          </div>

          {/* Why Recommended */}
          <div className="modal-section modal-reason-section">
            <h3 className="modal-section-title">🎯 Why This Was Recommended</h3>
            <div className="modal-reason-card">
              <div className="reason-similarity-bar">
                <div className="reason-similarity-fill" style={{ width: `${Math.min(similarity, 100)}%` }} />
                <span className="reason-similarity-label">{similarity}% Match</span>
              </div>
              <ul className="reason-list">
                {reasons.map((r, i) => (
                  <li key={i} className="reason-item">
                    <span className="reason-bullet">→</span> {r}
                  </li>
                ))}
              </ul>
              <p className="reason-explanation">
                Our recommendation engine uses <strong>cosine similarity</strong> on movie
                overviews and genres to find movies with the most similar content profile
                to your selection.
              </p>
            </div>
          </div>

          {/* Cast */}
          {detail?.cast && detail.cast.length > 0 && (
            <div className="modal-section">
              <h3 className="modal-section-title">🎭 Cast</h3>
              <div className="modal-cast-grid">
                {detail.cast.map((member) => (
                  <div className="cast-card" key={member.name + member.character}>
                    {member.photo ? (
                      <img src={member.photo} alt={member.name} className="cast-photo" loading="lazy" />
                    ) : (
                      <div className="cast-photo-placeholder">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                          <circle cx="12" cy="7" r="4" />
                        </svg>
                      </div>
                    )}
                    <p className="cast-name">{member.name}</p>
                    <p className="cast-character">{member.character}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Loading indicator for additional details */}
          {isLoadingDetail && (
            <div className="modal-loading">
              <div className="loading-spinner" />
              <span>Loading cast & crew...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MovieModal;
