interface TransparentCardProps {
  imageUrl?: string;
  subHeading?: string;
  description?: string;
}

function TransparentCard({
  imageUrl,
  subHeading,
  description,
}: TransparentCardProps) {
  return (
    <div className="w-full min-w-[200px] justify-baseline items-center md:p-10">
      {imageUrl && (
        <div className="w-full h-48 md:h-56 lg:h-76 overflow-hidden flex justify-center items-center rounded-md mb-3">
          <img
            src={imageUrl}
            alt="Transparent Card Background"
            className="w-full h-full object-cover block"
          />
        </div>
      )}
      <div className="py-4 ">
        <h2 className="text-base font-normal mb-2">{subHeading}</h2>
        <p className="text-gray-600 text-sm font-light">{description}</p>
      </div>
    </div>
  );
}

export default TransparentCard;
