import imgUrl from "../assets/images/fujiphilm-VgU5zIEy57A-unsplash.jpg";
import TransparentCard from "../components/TransparentCard";

const sampleCards = [
  {
    imageUrl: imgUrl,
    subHeading: "Top Headlines Every Day",
    description:
      "We fetch the world's most relevant news and filter for relevance.",
  },
  {
    imageUrl: imgUrl,
    subHeading: "Popularity Insights",
    description:
      "We analyze trending topics so you'll biw what's popular nowadays.",
  },
];

function SeeAlsoSection() {
  return (
    <div className="md:w-full lg:p-5 mb-10 gap-4">
      <h1 className="ml-3 text-2xl font-bold">See also</h1>
      <div className="h-full flex flex-row overflow-x-auto items-center gap-4 md:h-fit md:grid md:grid-cols-2 md:grid-rows-1 md:gap-2 md:overflow-x-visible p-5">
        {sampleCards.map((card, index) => (
          <TransparentCard
            key={index}
            imageUrl={card.imageUrl}
            subHeading={card.subHeading}
            description={card.description}
          />
        ))}
      </div>
    </div>
  );
}

export default SeeAlsoSection;
