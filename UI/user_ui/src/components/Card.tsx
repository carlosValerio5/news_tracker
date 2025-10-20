export interface NewsEntry {
  headline: string;
  summary: string;
  url: string;
  peak_interest: number;
  current_interest: number;
  thumbnail?: string;
}

function Card({ newsEntry }: { newsEntry: NewsEntry }) {
  return (
    <div
      className="
    p-5 py-10 flex flex-col 
    justify-between mb-5 ml-1.5 
    mr-0 shadow-xl min-w-[200px] 
    max-h-[500px] 
    w-full sm:w-80 md:w-96 lg:w-[500px] 
    rounded-2xl flex-none
    lg:max-h-fit
    "
    >
      {newsEntry.thumbnail && (
        <div className="w-full overflow-hidden rounded-2xl mb-4 flex-none">
          <img
            src={newsEntry.thumbnail}
            alt={newsEntry.headline}
            loading="lazy"
            className="w-full h-48 sm:h-64 md:h-52 lg:h-64 object-cover transition-opacity duration-300"
          />
        </div>
      )}
      <div className="flex flex-col">
        <h3 className="font-medium text-base text-text-principal sm:text-xl">
          {newsEntry.headline}
        </h3>
        <p className="text-sm sm:text-lg tracking-tight text-text-secondary hidden lg:block">
          {newsEntry.summary}
        </p>
        <a
          className="text-xs sm:text-sm text-blue-500 mt-2"
          href={newsEntry.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Read more
        </a>
      </div>
      <div className="flex flex-col lg:mt-5">
        <p className="text-sm sm:text-base">
          Peak Interest: {newsEntry.peak_interest}
        </p>
        <p className="text-sm sm:text-base">
          Current Interest: {newsEntry.current_interest}
        </p>
      </div>
    </div>
  );
}

export default Card;
