import RegisterButton from "../components/RegisterButton";
import { ButtonType } from "../components/RegisterButton";

function Hero() {
  return (
    <section
      className="w-full min-h-screen flex items-center sm:ml-5 sm:mt-0 mb-6"
      aria-label="Hero"
    >
      <div className="p-6 md:p-12 max-w-4xl ml-3 sm:ml-6 text-left rounded">
        <h1 className="text-3xl font-bold sm:text-5xl text-white">
          Stay Tuned With Zero Manual Effort
        </h1>
        <p className="mt-4 text-gray-400 font-light text-sm sm:text-base">
          Register to be notified about the latest news.
        </p>
        <div className="mt-6">
          <RegisterButton type={ButtonType.PRIMARY} />
        </div>
      </div>
    </section>
  );
}

export default Hero;
