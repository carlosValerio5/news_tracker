import NewsReport from './components/NewsReport'
import news from '../newsReportExample.json'

function SampleReport() {
  return (
    <div className='w-screen h-screen min-h-screen min-w-screen'>
        <NewsReport news={news} />
    </div>
  )
}

export default SampleReport