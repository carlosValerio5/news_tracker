import React from 'react'
import RegisterButton from '../components/RegisterButton';

function FeaturesSection() {
  return (
    <div className='pb-10'>
        <h1 className='font-bold text-2xl ml-3 pb-3 mb-3 px-3'>How We Keep You Updated</h1>
        <div className='mb-5 flex flex-col md:grid md:grid-cols-2 md:grid-rows-1 items-center'>
            <div className='px-8 py-3 max-w-md flex flex-col lg:gap-4'>
                <div>
                    <h2 className='mb-2'>Gather Reliable Information</h2>
                    <p className='text-gray-summary'>The information is gathered from reliable sources with a strong reputation.</p>
                </div>
                <div>
                    <h2 className='mb-2'>Analyze Popularity</h2>
                    <p className='text-gray-summary'>We estimate the popularity of latest news using Google Trends</p>
                </div>
                <div>
                    <h2 className='mb-2'>Deliver Daily Digest</h2>
                    <p className='text-gray-summary'>We provide a daily digest of the most important news updates.</p>
                </div>
            </div>
            <div className='max-h-[200px] overflow-clip hidden md:block md:max-h-[400px]'>
                <img className='rounded-sm' src='/src/assets/images/fujiphilm-VgU5zIEy57A-unsplash.jpg'></img>
            </div>
        </div>
        
        <RegisterButton type='SECONDARY' text='Get Started' />        
        <button className='ml-3 bg-gray-50 text-black text-xs p-2 rounded-sm border-gray-50 border-2 hover:bg-black hover:border-black hover:text-white'>See sample Report</button>
    </div>
  )
}

export default FeaturesSection