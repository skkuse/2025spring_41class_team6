import MainIntro from "@/components/layout/MainIntro";
import LoginForm from "@/components/layout/LoginForm";

const MainPage = () => {
  return (
    <div className="flex h-screen">
      <MainIntro />
      <LoginForm />
    </div>
  );
};

export default MainPage;
