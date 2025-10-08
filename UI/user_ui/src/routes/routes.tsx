import { createBrowserRouter } from "react-router-dom";
import Landing from "../Landing";
import News from "../News";
import SampleReport from "../SampleReport";
import Register from "../core/RegisterPage";
import Login from "../core/LoginPage";
import AdminDashboard from "../core/AdminDashboard";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Landing />,
  },
  {
    path: "/news",
    element: <News />,
  },
  {
    path: "/report-sample",
    element: <SampleReport />,
  },
  {
    path: "/register",
    element: <Register />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/report-sample",
    element: <SampleReport />,
  },
  {
    path: "/admin/dashboard",
    element: <AdminDashboard />,
  },
]);
