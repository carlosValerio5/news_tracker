import React from 'react'
import RegisterButton from './RegisterButton';

function SubscribeStrip() {
  return (
    <div className='flex flex-row justify-between p-5 items-center bg-[#F7F7F7] w-full'>
        <h1 className='text-xl'>Get Tomorrow's News Digest Direct to Your Mailbox</h1>
        <div className='flex flex-row pr-8'>
            <RegisterButton type='PRIMARY' text='Subscribe'/> 
            <button className='text-base ml-3 bg-gray-50 text-black p-2 rounded-sm border-gray-50 border-2 hover:bg-black hover:border-black hover:text-white'>Sample Report</button>
        </div>
    </div>
  )
}

export default SubscribeStrip