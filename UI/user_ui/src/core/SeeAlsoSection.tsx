import React from 'react'
import TransparentCard from '../components/TransparentCard'

const sampleCards = [
    {
        imageUrl: '/src/assets/images/fujiphilm-VgU5zIEy57A-unsplash.jpg',
        subHeading: 'Top Headlines Every Day',
        description: 'We fetch the world\'s most relevant news and filter for relevance.'
    },
    {
        imageUrl: '/src/assets/images/fujiphilm-VgU5zIEy57A-unsplash.jpg',
        subHeading: 'Popularity Insights',
        description: 'We analyze trending topics so you\'ll biw what\'s popular nowadays.'
    }
]

function SeeAlsoSection() {
  return (
    <div>
        <h1 className='ml-3 text-2xl font-bold'>
            See also
        </h1>
        <div className='flex flex-row overflow-x-auto items-center gap-4 md:h-fit md:grid md:grid-cols-2 md:grid-rows-1 md:gap-2 md:overflow-x-visible p-5'>
            {sampleCards.map((card, index) => (
                <TransparentCard 
                    key={index}
                    imageUrl={card.imageUrl}
                    subHeading={card.subHeading}
                    description={card.description}
                />
            ))}
        </div>
    </div>
  )
}

export default SeeAlsoSection