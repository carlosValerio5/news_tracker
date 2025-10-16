import news from "../../newsReportExample.json";
import NewsCard from "../components/NewsCard";
import { apiClient, type ApiResponse } from "../services/api";
import { useEffect, useState, useRef, useCallback } from "react";
import type { Article } from "../types/news";
import { isArticle } from "../types/news";
import type { LoadingState } from "../types/news";

function fetchNews() {
  return apiClient.get("/news-report");
}

const imageCache = new Map<number, { loaded: boolean; image?: HTMLImageElement }>();

const preloadImages = async (articles: Article[]): Promise<Map<number, boolean>> => {
  const imageLoadPromises = articles.filter(article => article.thumbnail!== undefined)
  .map(article => {
    if (!article.thumbnail) return Promise.resolve({ loaded: false });
    return preloadSingleImage(article.thumbnail, article.id);
  });

  const results = await Promise.allSettled(imageLoadPromises);
  const imageStatus = new Map<number, boolean>();

  results.forEach((result, index) => {
    const article = articles.filter(article => article.thumbnail!== undefined)[index];
    if (result.status === "fulfilled") {
      imageStatus.set(article.id, result.value.loaded);
      if (result.value.loaded)
        imageCache.set(article.id, result.value);
    }
    else {
      imageStatus.set(article.id, false);
    }
  });
  return imageStatus;
}

const preloadSingleImage = (imageUrl: string, articleId: number): Promise<{ loaded: boolean; image?: HTMLImageElement }> => {
  if(imageCache.has(articleId)) {
    return Promise.resolve(imageCache.get(articleId)!);
  }
  return new Promise((resolve) => {
    const img = new Image();
        
    const handleLoad = () => {
      cleanup();
      resolve({ loaded: true, image: img });
    };

    const handleError = (error: Event) => {
      cleanup();
      console.error(`Error loading image for article ${articleId}:`, error);
      console.warn(`Failed to load image for article ${articleId}: ${imageUrl}`);
      resolve({ loaded: false });
    };
    
    const handleTimeout = () => {
      cleanup();
      console.warn(`Image load timeout for article ${articleId}`);
      resolve({ loaded: false });
    };
    
    const cleanup = () => {
      img.removeEventListener('load', handleLoad);
      img.removeEventListener('error', handleError);
      clearTimeout(timeoutId);
    };
    
    img.addEventListener('load', handleLoad);
    img.addEventListener('error', handleError);
    
    // Set timeout for slow loading images
    const timeoutId = setTimeout(handleTimeout, 10000); // 10 seconds
    
    img.src = imageUrl;
  });
};


function NewsCardsSection() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: true,
    error: null,
    imagesLoaded: new Set<number>(),
    failedImages: new Set<number>(),
  });

  const mountedRef = useRef(true);

  const updateImageLoadingState = useCallback((articleId: number, success: boolean) => {
    if (!mountedRef.current) return;

    setLoadingState((prevState) => ({
      ...prevState,
      imagesLoaded: success ? new Set(prevState.imagesLoaded).add(articleId) : prevState.imagesLoaded,
      failedImages: !success ? new Set(prevState.failedImages).add(articleId) : prevState.failedImages,
    }));
  }, []);

  const loadNewsAndImages = useCallback(async () => {
    try{
      setLoadingState((prev) => ({ ...prev, isLoading: true, error: null }));

      const response = await fetchNews() as ApiResponse<Article[]>;
      if (!response) {
        throw new Error("No response from API");
      }
      if (!response.ok)
        throw new Error(`Failed to fetch news: ${response.status}`);

      if (!Array.isArray(response.data)) {
        throw new Error("Invalid data format from API");
      }

      const fetchedArticles: Article[] = response.data.filter(isArticle);
      
      console.log("Fetched articles from API:", fetchedArticles);

      if (!mountedRef.current) return;

      setArticles(fetchedArticles);
      setLoadingState((prev) => ({ ...prev, isLoading: false }));

      console.log("Fetched articles:", fetchedArticles);

      if (fetchedArticles.length > 0) {
        const criticalArticles = fetchedArticles.slice(0, 5);
        const remainingArticles = fetchedArticles.slice(5);

        preloadImages(criticalArticles).then((imageStatus) => {
          if (!mountedRef.current) return;

          imageStatus.forEach((loaded, articleId) => {
            updateImageLoadingState(articleId, loaded);
          });
        });

        setTimeout(() => {
          preloadImages(remainingArticles).then((imageStatus) => {
            if (!mountedRef.current) return;
            
            imageStatus.forEach((loaded, articleId) => {
              updateImageLoadingState(articleId, loaded);
            });
          });
        }, 500);
      }

    } catch (error) {
      if (!mountedRef.current) return;
      console.error("Error fetching news:", error);

      const fallbackArticles: Article[] = news.filter(isArticle);
      setArticles(fallbackArticles);
      setLoadingState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to load latest news",
        imagesLoaded: new Set<number>(),
        failedImages: new Set<number>(),
      }));

      if (fallbackArticles.length > 0) {
        preloadImages(fallbackArticles).then((imageStatus) => {
          if (!mountedRef.current) return;
          
          imageStatus.forEach((loaded, articleId) => {
            updateImageLoadingState(articleId, loaded);
          });
        });
      }
    }
  }, [updateImageLoadingState]);

  useEffect(() => {
    mountedRef.current = true;
    loadNewsAndImages();
    return () => {
      mountedRef.current = false;
    };
  }, [loadNewsAndImages]);

  //Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  if (loadingState.isLoading && articles.length === 0) {
    return <div className="p-5">Loading latest news...</div>;
  }

  if (loadingState.error && articles.length === 0) {
    return <div className="p-5 text-red-600">{loadingState.error}</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold ml-5 md:ml-10 lg:ml-15">Explore</h1>
      <div className="flex flex-col md:grid md:grid-cols-2 lg:grid-cols-3 lg:p-10">
        {articles &&
          articles.map((article, index) => (
            <NewsCard 
            key={index} 
            article={article} 
            imageLoaded={loadingState.imagesLoaded.has(article.id)} 
            imageFailed={loadingState.failedImages.has(article.id)}
            priority = {index < 5} />
          ))}
      </div>
    </div>
  );
}

export default NewsCardsSection;
