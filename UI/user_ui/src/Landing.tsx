import { useEffect, useRef, useState } from "react";
import NavBar from "./components/NavBar";
import Hero from "./core/Hero";
import LatestNewsSection from "./core/LatestNewsSection";
import FeaturesSection from "./core/FeaturesSection";
import SeeAlsoSection from "./core/SeeAlsoSection";
import SubscribeStrip from "./components/SubscribeStrip";
import Footer from "./components/Footer";
import { CDN_DOMAIN_NAME } from "./env";

const heroBg = `https://${CDN_DOMAIN_NAME}/landing/hero-background.jpg`;

function Landing() {
  const [faded, setFaded] = useState(false);
  const ticking = useRef(false);

  useEffect(() => {
    function onScroll() {
      if (!ticking.current) {
        window.requestAnimationFrame(() => {
          // Fade out the background over the first viewport height
          const progress = Math.min(window.scrollY / window.innerHeight, 1);
          setFaded(progress >= 0.1);
          ticking.current = false;
        });
        ticking.current = true;
      }
    }

    // initial check
    setFaded(window.scrollY >= window.innerHeight);

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="relative">
      {/* Full-viewport solid black background that fades after one screen */}
      <div
        aria-hidden="true"
        className={`fixed inset-x-0 top-0 h-screen bg-cover bg-center transition-opacity duration-700 ease-in-out pointer-events-none ${
          faded ? "opacity-0" : "opacity-100"
        }`}
        style={{
          backgroundImage: `url(${heroBg})`,
          backgroundColor: "#000", // fallback while image loads
        }}
      />

      <NavBar scroll={true} />
      <main className="relative z-10">
        <Hero />
        <LatestNewsSection />
        <FeaturesSection />
        <SeeAlsoSection />
        <SubscribeStrip />
        <Footer />
      </main>
    </div>
  );
}

export default Landing;
