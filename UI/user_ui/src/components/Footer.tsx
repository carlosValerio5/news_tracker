import React from 'react'

function Footer() {
  return (
    <footer className="w-full bg-gray-100 text-gray-600 text-center py-6 border-t border-gray-300 mt-1.5">
      <div className='flex items-center justify-evenly mb-10'>
        <p className='text-lg font-semibold'>NewsTracker</p>
        <div className="mb-2 grid grid-cols-2 gap-3 items-center pr-20">
            <a href="/about" className="mx-2 hover:underline text-sm">About</a>
            <a href="/privacy" className="mx-2 hover:underline text-sm">Privacy Policy</a>
            <a href="/terms" className="mx-2 hover:underline text-sm">Terms of Service</a>
            <a href="/contact" className="mx-2 hover:underline text-sm">Contact</a>
        </div>
      </div>
    <div className="text-xs">
        © 2025 News Tracker. All rights reserved.
    </div>
    </footer>
  )
}

export default Footer