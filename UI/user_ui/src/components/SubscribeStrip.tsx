import RegisterButton from "./RegisterButton";
import ReportButton from "./ReportButton";

function SubscribeStrip() {
  return (
    <div className="flex flex-row justify-between  p-5 items-center bg-[#F7F7F7] w-full">
      <h1 className="text-xs md:text-xl">
        Get Tomorrow's News Digest Direct to Your Mailbox
      </h1>
      <div className="flex flex-row md:pr-8 justify-between items-center">
        <span className="hidden md:block">
          <RegisterButton type="PRIMARY" text="Subscribe" className="ml-3" />
        </span>
        <span className="block md:hidden">
          <RegisterButton type="SECONDARY" text="Subscribe" className="ml-3" />
        </span>
        <ReportButton className="ml-3" />
      </div>
    </div>
  );
}

export default SubscribeStrip;
