import { createBrowserRouter } from "react-router-dom";
import Chat from "@/pages/Chat";
import History from "@/pages/History";
import MainPage from "@/pages/MainPage";

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
]);

export default router;
