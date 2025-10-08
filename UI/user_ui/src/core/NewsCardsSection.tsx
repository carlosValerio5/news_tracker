import news from "../../newsReportExample.json";
import NewsCard from "../components/NewsCard";
import { apiClient } from "../services/api";
import { useEffect, useState } from "react";
import type { Article } from "../types/news";
import { isArticle } from "../types/news";

function fetchNews() {
  return apiClient.get("/news-report");
}

function NewsCardsSection() {
  const [articles, setArticles] = useState<Article[]>([]);

  useEffect(() => {
    fetchNews()
      .then(async (response) => {
        if (!response) {
          console.error("No response from API");
          return;
        }
        console.log(response);
        if (!response.ok)
          throw new Error(`Failed to fetch news: ${response.statusText}`);
        const articles: Article[] = await response.json();
        setArticles(articles.filter(isArticle));
        console.log("Fetched articles:", articles);
      })
      .catch((error) => {
        console.error("Error fetching news:", error);
        setArticles(news); // Fallback to local news on error
      });
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold ml-5 md:ml-10 lg:ml-15">Explore</h1>
      <div className="flex flex-col md:grid md:grid-cols-2 lg:p-10">
        {articles &&
          articles.map((article, index) => (
            <NewsCard key={index} article={article} />
          ))}
      </div>
    </div>
  );
}

export default NewsCardsSection;
