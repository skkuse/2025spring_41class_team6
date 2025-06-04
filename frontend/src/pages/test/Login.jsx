import { registerUser, loginUser, logoutUser } from "@/apis/auth/auth";
import { useState } from "react";
import { getUserInfo } from "@/apis/auth/getUserInfo";

const Login = () => {
  const [registerForm, setRegisterForm] = useState({
    email: "",
    password: "",
    nickname: "",
  });
  const [loginForm, setLoginForm] = useState({
    email: "",
    password: "",
  });
  const [showRegister, setShowRegister] = useState(false);
  const [showLogin, setShowLogin] = useState(false);

  const [userInfo, setUserInfo] = useState(null);

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await registerUser({ ...registerForm, login: false });
      console.log("회원가입 성공:", response);
      alert("회원가입이 완료되었습니다!");
    } catch (error) {
      console.error("회원가입 실패:", error);
      alert("회원가입에 실패했습니다.");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await loginUser(loginForm);
      console.log("로그인 성공:", response);
      alert("로그인이 완료되었습니다!");
    } catch (error) {
      console.error("로그인 실패:", error);
      alert("로그인에 실패했습니다.");
    }
  };

  const handleLogout = async () => {
    try {
      const response = await logoutUser();
      console.log("로그아웃 성공:", response);
      alert("로그아웃이 완료되었습니다!");
    } catch (error) {
      console.error("로그아웃 실패:", error);
      alert("로그아웃에 실패했습니다.");
    }
  };

  const handleGetUserInfo = async () => {
    const response = await getUserInfo();
    setUserInfo(response);
  };

  return (
    <div className="p-5">
      <h1 className="text-2xl font-bold mb-5">Test</h1>

      {/* 회원가입 토글 버튼 */}
      <div className="mb-4">
        <button
          onClick={() => setShowRegister(!showRegister)}
          className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors flex items-center justify-between"
        >
          <span>회원가입</span>
          <span>{showRegister ? "▲" : "▼"}</span>
        </button>

        {showRegister && (
          <div className="mt-3 p-4 border rounded-md bg-white">
            <form onSubmit={handleRegister} className="space-y-3">
              <div>
                <input
                  type=""
                  placeholder="이메일"
                  className="w-full px-4 py-2 border rounded-md"
                  value={registerForm.email}
                  onChange={(e) =>
                    setRegisterForm({ ...registerForm, email: e.target.value })
                  }
                />
              </div>
              <div>
                <input
                  type="password"
                  placeholder="비밀번호"
                  className="w-full px-4 py-2 border rounded-md"
                  value={registerForm.password}
                  onChange={(e) =>
                    setRegisterForm({
                      ...registerForm,
                      password: e.target.value,
                    })
                  }
                />
              </div>
              <div>
                <input
                  type="text"
                  placeholder="닉네임"
                  className="w-full px-4 py-2 border rounded-md"
                  value={registerForm.nickname}
                  onChange={(e) =>
                    setRegisterForm({
                      ...registerForm,
                      nickname: e.target.value,
                    })
                  }
                />
              </div>
              <button
                type="submit"
                className="w-full px-5 py-2.5 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors"
              >
                회원가입
              </button>
            </form>
          </div>
        )}
      </div>

      {/* 로그인 토글 버튼 */}
      <div className="mb-4">
        <button
          onClick={() => setShowLogin(!showLogin)}
          className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors flex items-center justify-between"
        >
          <span>로그인</span>
          <span>{showLogin ? "▲" : "▼"}</span>
        </button>

        {showLogin && (
          <div className="mt-3 p-4 border rounded-md bg-white">
            <form onSubmit={handleLogin} className="space-y-3">
              <div>
                <input
                  type=""
                  placeholder="이메일"
                  className="w-full px-4 py-2 border rounded-md"
                  value={loginForm.email}
                  onChange={(e) =>
                    setLoginForm({ ...loginForm, email: e.target.value })
                  }
                />
              </div>
              <div>
                <input
                  type="password"
                  placeholder="비밀번호"
                  className="w-full px-4 py-2 border rounded-md"
                  value={loginForm.password}
                  onChange={(e) =>
                    setLoginForm({ ...loginForm, password: e.target.value })
                  }
                />
              </div>
              <button
                type="submit"
                className="w-full px-5 py-2.5 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
              >
                로그인
              </button>
            </form>
          </div>
        )}
      </div>

      {/* 로그아웃 버튼 */}
      <div>
        <button
          onClick={handleLogout}
          className="w-full px-5 py-2.5 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors"
        >
          로그아웃
        </button>
      </div>
      <div>
        <button onClick={handleGetUserInfo}>사용자 정보 조회</button>
        {userInfo && (
          <div>
            <p>id: {userInfo.id}</p>
            <p>email: {userInfo.email}</p>
            <p>nickname: {userInfo.nickname}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;
