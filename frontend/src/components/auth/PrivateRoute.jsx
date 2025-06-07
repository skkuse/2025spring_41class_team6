// components/auth/PrivateLayout.tsx
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { getUserInfo } from "@/apis/auth/getUserInfo";

const PrivateLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userInfo = await getUserInfo();
        if (!userInfo) {
          alert("로그인이 필요한 서비스입니다.");
          navigate("/", { state: { from: location.pathname } });
        }
      } catch {
        alert("로그인이 필요한 서비스입니다.");
        navigate("/", { state: { from: location.pathname } });
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, [navigate, location.pathname]);

  if (isLoading) return <div>Loading…</div>;
  return <Outlet />;
};

export default PrivateLayout;
