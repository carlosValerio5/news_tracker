export interface NewsEntry{
    headline: string,
    summary: string,
    url: string,
    peak_interest: number,
    current_interest: number,
}

function Card({newsEntry}: {newsEntry: NewsEntry}) {
  return (
    <div className='
    p-5 py-10 flex flex-col 
    justify-between mb-5 ml-1.5 
    mr-0 shadow-xl min-w-[200px] 
    h-[250px] sm:h-[300px] sm:min-w-[300px] sm:max-w-[350px]
    rounded-2xl
    '>
      <div className='flex flex-col'>
        <h3 className='font-medium text-base sm:text-xl'>{newsEntry.headline}</h3>
        <p className='text-sm sm:text-xl text-gray-summary'>{newsEntry.summary}</p>
        <a className='text-xs sm:text-sm' href={newsEntry.url} target="_blank" rel="noopener noreferrer">Read more</a>
      </div>
      <div className='flex flex-col'>
        <p className='text-sm sm:text-base'>Peak Interest: {newsEntry.peak_interest}</p>
        <p className='text-sm sm:text-base'>Current Interest: {newsEntry.current_interest}</p>
      </div>
    </div>
  )
}

export default Card