import type { Article } from "../types/news";

function NewsReport({ news }: { news: Article[] }) {
  return (
    <div className="p-20 bg-gray-100 h-full flex flex-col gap-5 justify-center">
      <h2 className="text-[#004080]">📊 News Update</h2>
      {news.map((item, index) => (
        <div key={index} className="mb-20px">
          <h3 className="text-[#333]">{item.headline}</h3>
          <p className="text-[#555]">{item.summary}</p>
          <p className="text-[12px] text-gray-500">
            Peak Interest: {item.peak_interest} | Current Interest:{" "}
            {item.current_interest}
          </p>
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500"
          >
            Read more
          </a>
        </div>
      ))}
    </div>
  );
}

export default NewsReport;
