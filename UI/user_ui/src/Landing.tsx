import NavBar from './components/NavBar';
import Hero from './core/Hero';
import LatestNewsSection from './core/LatestNewsSection';
import FeaturesSection from './core/FeaturesSection';
import SeeAlsoSection from './core/SeeAlsoSection';
import SubscribeStrip from './components/SubscribeStrip';
import Footer from './components/Footer';

function Landing() {
  return (
    <div>
      <NavBar />
      <Hero />
      <LatestNewsSection />
      <FeaturesSection />
      <SeeAlsoSection />
      <SubscribeStrip />
      <Footer />
    </div>
  )
}

export default Landing 