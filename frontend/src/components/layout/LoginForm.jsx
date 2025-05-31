import { useState, useEffect } from "react";

const LoginForm = () => {
  const [activeTab, setActiveTab] = useState("login");

  // useEffect(() => {
  //   console.log(`Active tab changed to: ${activeTab}`);
  // }, [activeTab]);

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
            className={`flex-1 text-center py-2 font-semibold border-b-2 border-black ${
              activeTab === "login"
                ? "border-black text-black"
                : "border-transparent text-gray-500"
            }`}
            onClick={() => setActiveTab("login")}
          >
            로그인
          </button>
          <button
            className={`flex-1 text-center py-2 font-semibold border-b-2 border-black ${
              activeTab === "signup"
                ? "border-black text-black"
                : "border-transparent text-gray-500"
            }`}
            onClick={() => setActiveTab("signup")}
          >
            회원가입
          </button>
        </div>

        {/* Email / PassWord */}
        <input
          type="email"
          placeholder="your@email.com"
          className="w-full px-4 py-2 mb-3 border rounded"
        />
        <input
          type="password"
          placeholder="비밀번호를 입력하세요"
          className="w-full px-4 py-2 mb-3 border rounded"
        />

        {/* Maintain login / Find Password */}
        <div className="flex justify-between items-center text-sm mb-4">
          <label className="flex items-center space-x-2">
            <input type="checkbox" />
            <span>로그인 상태 유지</span>
          </label>
          <a href="#" className="text-blue-500">
            비밀번호 찾기
          </a>
        </div>

        {/* Login Button */}
        <button className="w-full bg-black text-white py-2 rounded mb-4">
          로그인
        </button>

        {/* Login With Google */}
        <button className="w-full border py-2 rounded flex items-center justify-center space-x-2">
          <span>G</span>
          <span>Google로 계속하기</span>
        </button>
      </div>
    </div>
  );
};

export default LoginForm;
