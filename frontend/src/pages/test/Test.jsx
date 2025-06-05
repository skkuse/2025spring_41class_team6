import Login from "./Login";
import { useNavigate } from "react-router-dom";

const Test = () => {
  const navigate = useNavigate();
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <button
        onClick={() => navigate("/test/login")}
        className="bg-blue-500 text-white px-4 py-2 rounded-md"
      >
        로그인
      </button>
    </div>
  );
};

export default Test;
