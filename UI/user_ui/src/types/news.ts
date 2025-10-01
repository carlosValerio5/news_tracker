export interface Article {
    headline: string;
    summary: string;
    url: string;
    peak_interest: number;
    current_interest: number;
    news_section?: string;
}

export function isArticle(obj: any): obj is Article {
  return obj &&
    typeof obj.headline === 'string' &&
    typeof obj.summary === 'string' &&
    typeof obj.url === 'string' &&
    !isNaN(Number(obj.peak_interest)) &&
    !isNaN(Number(obj.current_interest)) &&
    (obj.news_section === undefined || typeof obj.news_section === 'string');
}