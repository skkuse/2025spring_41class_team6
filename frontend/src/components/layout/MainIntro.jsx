const MainIntro = () => {
  return (
    <div className="flex flex-col justify-center items-center flex-1 bg-white">
      <div className="text-center">
        <div className="text-3xl font-bold mb-2 flex items-center justify-center">
          <span className="mr-2 bg-black text-white px-2 py-1 rounded">▶</span>
          MovieChat
        </div>
        <div className="text-xl font-semibold mb-2">
          영화와 대화하는 새로운 방법
        </div>
        <div className="text-gray-500 mb-6 text-sm">
          AI와 함께 영화를 탐험하고, 당신만의 영화 세계를 만들어보세요
        </div>
        <div className="flex space-x-10 justify-center">
          <div className="text-center">
            <div className="text-lg font-bold">10K+</div>
            <div className="text-sm text-gray-600">영화</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold">5K+</div>
            <div className="text-sm text-gray-600">사용자</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainIntro;
