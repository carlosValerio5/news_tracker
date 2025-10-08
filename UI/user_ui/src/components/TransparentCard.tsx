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
    <div className="max-h-[600px] min-w-[200px] justify-baseline items-center md:p-10">
      {imageUrl && (
        <div className="h-full w-full overflow-clip flex justify-center items-center mb-3">
          <img
            src={imageUrl}
            alt="Transparent Card Background"
            className="w-full h-auto"
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
