import React from 'react'
import RegisterButton from '../components/RegisterButton'
import { ButtonType } from '../components/RegisterButton'

function Hero() {
  return (
    <div className='w-full sm:ml-5 sm:mt-10 mb-6'>
      <h1 className='ml-3 text-2xl font-bold sm:text-4xl'>Stay tuned</h1>
      <p className='ml-3 my-2 text-gray-500 font-light text-xs sm:text-base'>Register to be notified about the latest news.</p>
      <RegisterButton type={ButtonType.PRIMARY} />
      <div className='w-full p-10 lg:p-15 max-h-[400px] overflow-clip'>
        <img className='w-full h-auto mt-4 mx-auto' src="/src/assets/images/utsav-srestha-HeNrEdA4Zp4-unsplash.jpg" alt="newspaper image" />
      </div>
    </div>
  )
}

export default Hero