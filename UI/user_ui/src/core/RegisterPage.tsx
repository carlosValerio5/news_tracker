import { Link } from "react-router-dom";
import TitleBar from "../components/TitleBar";
import CustomGoogleLogin from "../components/CustomGoogleLogin";

function RegisterPage() {
  return (
    <div>
      <TitleBar />
      <div className="min-h-screen w-full flex pt-20 items-baseline md:items-center md:pt-0 justify-center bg-gray-50">
        <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8 flex flex-col items-center gap-4">
          <h1 className="text-2xl font-bold mb-2 text-black">Register</h1>
          <p className="mb-6 text-gray-500 text-sm">
            Create your account with Google.
          </p>
          <CustomGoogleLogin />
          <div className="mt-4 text-sm text-gray-500">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-black font-semibold hover:underline"
            >
              Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
