import { createBrowserRouter } from "react-router-dom";
import Chat from "@/pages/Chat";
import History from "@/pages/History";
import MainPage from "@/pages/MainPage";
import Test from "@/pages/test/Test";
import Login from "@/pages/test/Login";
const router = createBrowserRouter([
  {
    path: "/",
    element: <MainPage />,
  },
  {
    path: "/:chatId",
    element: <Chat />,
  },
  {
    path: "/history",
    element: <History />,
  },
  {
    path: "/history/:id",
    element: <History />,
  },
  {
    path: "/main",
    element: <MainPage />,
  },
  {
    path: "/test",
    children: [
      {
        path: "",
        element: <Test />,
      },
      {
        path: "login",
        element: <Login />,
      },
    ],
  },
]);

export default router;
