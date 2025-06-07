import { createBrowserRouter } from "react-router-dom";
import MainPage from "@/pages/MainPage";
import Chat from "@/pages/Chat";
import History from "@/pages/History";
import Test from "@/pages/test/Test";
import Login from "@/pages/test/Login";
import PrivateRoute from "@/components/auth/PrivateRoute";

const router = createBrowserRouter([
  { path: "/", element: <MainPage /> },
  {
    path: "chat",
    element: <PrivateRoute />,
    children: [
      { index: true, element: <Chat /> },
      { path: ":chatId", element: <Chat /> },
    ],
  },
  {
    path: "history",
    element: <PrivateRoute />,
    children: [
      { index: true, element: <History /> },
      { path: ":id", element: <History /> },
    ],
  },
  {
    path: "test",
    children: [
      { index: true, element: <Test /> },
      { path: "login", element: <Login /> },
    ],
  },
  // optionally redirect /main → /
  { path: "main", element: <MainPage /> },
]);

export default router;
