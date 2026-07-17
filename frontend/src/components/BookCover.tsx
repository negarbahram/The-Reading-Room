import { useState } from 'react';

interface BookCoverProps {
  coverUrl: string;
  title: string;
  className?: string;
}

/** Book-cover image with a loading skeleton and a clean typographic fallback
 * for books with a missing `cover_url`, or whose remote image fails to load
 * or is slow to arrive at runtime. */
export function BookCover({ coverUrl, title, className = '' }: BookCoverProps) {
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);
  const hasSource = Boolean(coverUrl) && !failed;

  if (!hasSource) {
    return (
      <span className="font-serif text-parchment-100 text-center px-3 text-sm leading-snug">
        {title}
      </span>
    );
  }

  return (
    <div className="relative w-full h-full">
      {!loaded && <div className={`skeleton absolute inset-0 ${className}`} aria-hidden="true" />}
      <img
        src={coverUrl}
        alt={`Cover of ${title}`}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        onError={() => setFailed(true)}
        className={`w-full h-full object-cover transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'} ${className}`}
      />
    </div>
  );
}
