import { createBrowserRouter } from 'react-router-dom';
import Landing from '../Landing';
import News from '../News';


export const router = createBrowserRouter([
  {
    path: '/',
    element: <Landing />,
  },
  {
    path: '/news',
    element: <News />,
  }
]);