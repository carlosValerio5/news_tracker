import RegisterButton from '../components/RegisterButton';
import ReportButton from '../components/ReportButton';

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
        
        <div className='flex flex-row justify-start items-center gap-4 px-3'>
            <RegisterButton type='SECONDARY' text='Get Started' className='ml-3'/>        
            <ReportButton />
        </div>
    </div>
  )
}

export default FeaturesSection