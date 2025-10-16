import { useEffect, useState } from "react";
import { categoryIcons } from "../categoryIcons";
import { popularityRatings } from "../popularityRatings";
import type { Article } from "../types/news";

interface NewsCardProps {
  article: Article;
  imageLoaded: boolean;
  imageFailed: boolean;
  priority?: boolean;
}

function NewsCard({ article, imageLoaded, imageFailed, priority } : NewsCardProps) {
  const [imageState, setImageState] = useState<"loading" | "loaded" | "error">('loading');

  useEffect(() => {
    if (imageLoaded) {
      setImageState('loaded');
    } else if (imageFailed) {
      setImageState('error');
    } else {
      setImageState('loading');
    }
  }, [imageLoaded, imageFailed]);

  const handleImageLoaded = () => {
    setImageState('loaded');
  };

  const handleImageError = () => {
    setImageState('error');
  };

  return (
    <div className="flex flex-col justify-between shadow-lg p-10 m-5 bg-gray-300/20 max-w-[600px] h-auto min-h-[400px] md:min-h-[300px] lg:min-h[350px]">
            <div className="relative h-48 bg-gray-200">
        {imageState === 'loading' && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center">
              <div className="animate-pulse bg-gray-300 rounded w-16 h-16 mb-2"></div>
              <p className="text-sm text-gray-500">Loading image...</p>
            </div>
          </div>
        )}
        
        {imageState === 'error' && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-2">📷</div>
              <p className="text-sm">Image unavailable</p>
            </div>
          </div>
        )}

        {article.thumbnail && (
          <img
            src={article.thumbnail}
            alt={article.headline}
            className={`w-full h-full object-cover transition-opacity duration-300 ${
              imageState === 'loaded' ? 'opacity-100' : 'opacity-0'
            }`}
            onLoad={handleImageLoaded}
            onError={handleImageError}
            loading={priority ? "eager" : "lazy"} // Eager loading for priority images
          />
        )}
      </div>

      <div className="flex flex-col gap-3">
        <div className="flex flex-row justify-between items-center">
          <h2 className="text-lg font-semibold">{article.headline}</h2>
          {article.news_section && categoryIcons[article.news_section]
            ? categoryIcons[article.news_section]
            : categoryIcons["default"]}
        </div>
        <p className="text-sm">{article.summary}</p>
        <a className="text-blue-500" href={article.url}>
          Read more
        </a>
      </div>
      <div className="flex flex-row gap-5 items-center">
        <div className="flex flex-col justify-center">
          <p className="font-semibold">
            Peak Interest: {article.peak_interest}
          </p>
          <p className="font-semibold">
            Current Interest: {article.current_interest}
          </p>
        </div>
        {article.current_interest >= 75 ? (
          <div className="flex flex-row items-center gap-2 mt-2">
            {popularityRatings.high}
          </div>
        ) : article.current_interest >= 50 ? (
          <div className="flex flex-row items-center gap-2 mt-2">
            {popularityRatings.medium}
          </div>
        ) : (
          <div className="flex flex-row items-center gap-2 mt-2">
            {popularityRatings.low}
          </div>
        )}
      </div>
    </div>
  );
}

export default NewsCard;
