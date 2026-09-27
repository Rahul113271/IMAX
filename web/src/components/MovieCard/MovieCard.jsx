import './MovieCard.css';

const MovieCard = ({ movie, index, onClick }) => {
  const {
    title,
    poster,
    vote_average = 0,
    release_date = '',
    genres = [],
    similarity = 0,
    overview = '',
  } = movie;

  const year = release_date ? new Date(release_date).getFullYear() : '';

  const ratingClass =
    vote_average >= 7 ? 'high' : vote_average >= 5 ? 'mid' : 'low';

  return (
    <article
      className="movie-card"
      style={{ animationDelay: `${index * 0.05}s` }}
      onClick={() => onClick && onClick(movie)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter' && onClick) onClick(movie); }}
    >
      <div className="card-poster-wrap">
        <img
          className="card-poster"
          src={poster}
          alt={`${title} poster`}
          loading="lazy"
        />
        <div className="card-overlay">
          <span className={`card-rating rating-${ratingClass}`}>
            ★ {vote_average.toFixed(1)}
          </span>
          {similarity > 0 && (
            <span className="card-similarity">{similarity}% match</span>
          )}
        </div>
      </div>

      <div className="card-body">
        <h3 className="card-title">{title}</h3>
        <div className="card-meta">
          {year && <span className="card-year">{year}</span>}
          {genres.length > 0 && (
            <div className="card-genres">
              {genres.slice(0, 2).map((g) => (
                <span key={g} className="genre-tag">
                  {g}
                </span>
              ))}
            </div>
          )}
        </div>
        {overview && (
          <p className="card-overview">{overview.slice(0, 100)}{overview.length > 100 ? '…' : ''}</p>
        )}
      </div>
    </article>
  );
};

export default MovieCard;
