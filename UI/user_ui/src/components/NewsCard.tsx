import { categoryIcons } from "../categoryIcons";
import { popularityRatings } from "../popularityRatings";
import type { Article } from "../types/news";

function NewsCard({ article }: { article: Article }) {
  return (
    <div className="flex flex-col justify-between shadow-lg p-10 m-5 bg-gray-300/20 max-w-[600px] h-auto min-h-[400px] md:min-h-[300px] lg:min-h[350px]">
      <div className="flex flex-col gap-3">
        <div className="flex flex-row gap-4 items-center">
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
