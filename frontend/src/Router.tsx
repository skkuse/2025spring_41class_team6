import { createBrowserRouter } from "react-router-dom";
import Chat from "@/pages/Chat";
import Bookmark from "@/pages/Bookmark";
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
    path: "/bookmark",
    element: <Bookmark />,
  },
  {
    path: "/history",
    element: <History />,
  },
]);

export default router;
