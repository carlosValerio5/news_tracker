import Card from "../components/Card";
import news from "../../news_example.json";
import type { NewsEntry } from "../components/Card";

function LatestNewsSection() {
  return (
    <div className="w-full lg:p-5 sm:mt-10 mb-10 gap-4">
      <h1 className="ml-3 text-2xl font-bold col-span-3">Latest News</h1>
      <div className="pl-3 py-5 flex flex-row overflow-x-auto gap-4 lg:grid lg:grid-cols-3 lg:grid-rows-1 lg:gap-2 lg:overflow-x-visible">
        {news.slice(0, 3).map((item: NewsEntry) => (
          <Card key={item.url} newsEntry={item} />
        ))}
      </div>
    </div>
  );
}

export default LatestNewsSection;
