import { useState, useEffect } from "react";
import { registerUser, loginUser, logoutUser } from "@/apis/auth/auth";
import { getUserInfo } from "@/apis/auth/getUserInfo";
import { useNavigate } from "react-router-dom";

const LoginForm = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("login");
  const [registerForm, setRegisterForm] = useState({
    email: "",
    password: "",
    nickname: "",
  });
  const [loginForm, setLoginForm] = useState({
    email: "",
    password: "",
  });

  const checkLoginStatus = async () => {
    try {
      const userInfo = await getUserInfo();
      if (userInfo) {
        navigate("/chat");
      }
    } catch (error) {
      console.error("로그인 상태 확인 실패:", error);
    }
  };

  useEffect(() => {
    checkLoginStatus();
  }, [navigate]);

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await registerUser({ ...registerForm, login: true });
      alert("회원가입이 완료되었습니다!");
      setActiveTab("login");
      // 회원가입 후 로그인 상태 확인
      await checkLoginStatus();
    } catch (error) {
      console.error("회원가입 실패:", error);
      alert("회원가입에 실패했습니다.");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await loginUser(loginForm);
      alert("로그인이 완료되었습니다!");
      navigate("/chat");
    } catch (error) {
      console.error("로그인 실패:", error);
      alert("로그인에 실패했습니다.");
    }
  };

  const handleLogout = async () => {
    try {
      const response = await logoutUser();
      alert("로그아웃이 완료되었습니다!");
      navigate("/");
    } catch (error) {
      console.error("로그아웃 실패:", error);
      alert("로그아웃에 실패했습니다.");
    }
  };

  return (
    <div className="flex flex-col justify-center items-center w-[400px] border-l bg-[#f9f9f9] px-10">
      <div className="w-full">
        <h2 className="text-xl font-bold mb-4">시작하기</h2>
        <p className="text-sm text-gray-500 mb-6">
          영화의 새로운 세계로 떠나보세요
        </p>

        {/* Login / Sign in */}
        <div className="flex mb-4 border-b">
          <button
            className={`flex-1 text-center py-2 font-semibold border-b-2 ${
              activeTab === "login"
                ? "border-black text-black"
                : "border-transparent text-gray-500"
            }`}
            onClick={() => setActiveTab("login")}
          >
            로그인
          </button>
          <button
            className={`flex-1 text-center py-2 font-semibold border-b-2 ${
              activeTab === "signup"
                ? "border-black text-black"
                : "border-transparent text-gray-500"
            }`}
            onClick={() => setActiveTab("signup")}
          >
            회원가입
          </button>
        </div>

        {activeTab === "login" ? (
          <form onSubmit={handleLogin} className="space-y-3">
            <input
              type=""
              placeholder="your@email.com"
              className="w-full px-4 py-2 border rounded"
              value={loginForm.email}
              onChange={(e) =>
                setLoginForm({ ...loginForm, email: e.target.value })
              }
            />
            <input
              type="password"
              placeholder="비밀번호를 입력하세요"
              className="w-full px-4 py-2 border rounded"
              value={loginForm.password}
              onChange={(e) =>
                setLoginForm({ ...loginForm, password: e.target.value })
              }
            />
            <div className="flex justify-between items-center text-sm">
              <label className="flex items-center space-x-2">
                <input type="checkbox" />
                <span>로그인 상태 유지</span>
              </label>
              <a href="#" className="text-blue-500">
                비밀번호 찾기
              </a>
            </div>
            <button
              type="submit"
              className="w-full bg-black text-white py-2 rounded mb-4"
            >
              로그인
            </button>
            <button
              type="button"
              className="w-full border py-2 rounded flex items-center justify-center space-x-2"
            >
              <span>G</span>
              <span>Google로 계속하기</span>
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="space-y-3">
            <input
              type=""
              placeholder="your@email.com"
              className="w-full px-4 py-2 border rounded"
              value={registerForm.email}
              onChange={(e) =>
                setRegisterForm({ ...registerForm, email: e.target.value })
              }
            />
            <input
              type="password"
              placeholder="비밀번호를 입력하세요"
              className="w-full px-4 py-2 border rounded"
              value={registerForm.password}
              onChange={(e) =>
                setRegisterForm({ ...registerForm, password: e.target.value })
              }
            />
            <input
              type="text"
              placeholder="닉네임"
              className="w-full px-4 py-2 border rounded"
              value={registerForm.nickname}
              onChange={(e) =>
                setRegisterForm({ ...registerForm, nickname: e.target.value })
              }
            />
            <button
              type="submit"
              className="w-full bg-black text-white py-2 rounded mb-4"
            >
              회원가입
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default LoginForm;
