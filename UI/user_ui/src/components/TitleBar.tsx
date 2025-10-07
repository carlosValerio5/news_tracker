import { Link } from 'react-router-dom';

function TitleBar() {
  return (
    <div className="w-full fixed top-0 z-50 bg-gradient-to-r from-gray-50 via-gray-300 to-gray-200 shadow-md flex items-center justify-center py-4 px-6">
      <Link to="/" className="flex items-center gap-3">
        <span className="text-2xl sm:text-3xl font-light tracking-tight text-black drop-shadow-sm">NewsTracker</span>
      </Link>
    </div>
  )
}

export default TitleBar