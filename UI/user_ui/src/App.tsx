import React from 'react';
import { Router, RouterProvider, createBrowserRouter } from 'react-router-dom';
import Landing from './Landing';
import News from './News';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Landing />,
  },
  {
    path: '/news',
    element: <News />,
  }
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App