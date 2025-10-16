export interface Article {
  id: number;
  headline: string;
  summary: string;
  url: string;
  peak_interest: number;
  current_interest: number;
  news_section?: string;
  thumbnail?: string;
}

export function isArticle(obj: unknown): obj is Article {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "headline" in obj &&
    "summary" in obj &&
    "url" in obj &&
    typeof (obj as Record<string, unknown>).id === "number" &&
    typeof (obj as Record<string, unknown>).headline === "string" &&
    typeof (obj as Record<string, unknown>).summary === "string" &&
    typeof (obj as Record<string, unknown>).url === "string" &&
    !isNaN(Number((obj as Record<string, unknown>).peak_interest)) &&
    !isNaN(Number((obj as Record<string, unknown>).current_interest)) &&
    ((obj as Record<string, unknown>).news_section === undefined ||
      typeof (obj as Record<string, unknown>).news_section === "string")
  );
}

// Types for loading states
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  imagesLoaded: Set<number>;
  failedImages: Set<number>;
}