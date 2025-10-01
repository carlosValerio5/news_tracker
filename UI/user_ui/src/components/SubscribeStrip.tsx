import RegisterButton from './RegisterButton';

function SubscribeStrip() {
  return (
    <div className='flex flex-row justify-between  p-5 items-center bg-[#F7F7F7] w-full'>
      <h1 className='text-xs md:text-xl'>Get Tomorrow's News Digest Direct to Your Mailbox</h1>
      <div className='flex flex-row md:pr-8 justify-between'>
        <span className='hidden md:block'>
          <RegisterButton type='PRIMARY' text='Subscribe' />
        </span>
        <span className='block md:hidden'>
          <RegisterButton type='SECONDARY' text='Subscribe' />
        </span>
        <button className='text-xs md:text-base ml-3 bg-[#E6E6E6] text-black p-2 rounded-sm border-gray-50 border-2 hover:bg-black hover:border-black hover:text-white'>Sample Report</button>
      </div>
    </div>
  )
}

export default SubscribeStrip