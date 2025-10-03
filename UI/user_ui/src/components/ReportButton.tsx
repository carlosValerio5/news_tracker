import { Link } from 'react-router-dom'

function ReportButton({className}: {className?: string}) {
  return (
    <div>
  <Link to="/report-sample" className={`ml-3 min-w-[120px] whitespace-nowrap bg-gray-200 text-black text-xs sm:text-sm p-3 rounded-sm border-gray-50 border-2 hover:bg-black hover:border-black hover:text-white text-left ${className}`}>Sample Report</Link>
    </div>
  )
}

export default ReportButton