import { createBrowserRouter } from "react-router-dom";
import Chat from "@/pages/Chat";
import History from "@/pages/History";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Chat />,
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
]);

export default router;
