import React from 'react'
import news from '../../newsReportExample.json'
import NewsCard from '../components/NewsCard'


function NewsCardsSection() {
  return (
    <div>
        <h1 className='text-3xl font-bold ml-5 md:ml-10 lg:ml-15'>Explore</h1>
        <div className='flex flex-col md:grid md:grid-cols-2 lg:p-10'>
            {news.map((article, index) => (
                <NewsCard key={index} article={article} />
            ))}
        </div>
    </div>
  )
}

export default NewsCardsSection