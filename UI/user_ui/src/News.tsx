import NavBar from "./components/NavBar";
import Footer from "./components/Footer";
import NewsCardsSection from "./core/NewsCardsSection";

function News() {
  return (
    <div>
      <NavBar />
      <NewsCardsSection />
      <Footer fixed={true} />
    </div>
  );
}

export default News;
