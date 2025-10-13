import { Link } from "react-router-dom";

function AuthenticationFailed() {
  return (
    <div className="flex flex-col w-screen h-screen justify-center items-center gap-10 bg-dark">
      <div className="bg-gradient-to-t from-normal/30 to-light p-10 hover:from-normal rounded-2xl flex flex-col items-center justify-center gap-5 border border-border-color shadow-default">
        <h1 className="text-4xl text-red-500 font-semibold">
          Authentication Failed
        </h1>
        <p className="text-lg text-text-secondary">
          Please check your credentials and try again.
        </p>
        <Link
          to="/login"
          className="mt-4 px-4 py-2 bg-light text-text-principal border-border-color rounded border-t-highlight"
        >
          Go to Login
        </Link>
      </div>
    </div>
  );
}

export default AuthenticationFailed;
