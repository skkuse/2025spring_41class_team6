const getMovies = () => {
  return [
    {
      id: 1,
      title: "인센션",
      year: "2010",
      director: "크리스토퍼 놀란",
      description: "현실과 꿈의 경계를 넘나드는 액션 블록버스터",
      imageUrl: "",
    },
    {
      id: 2,
      title: "기생충",
      year: "2019",
      director: "봉준호",
      description: "두 가족의 만남으로 시작되는 예기치 못한 사건",
      imageUrl: "",
    },
    {
      id: 3,
      title: "어벤져서: 엔드게임",
      year: "2019",
      director: "안소니 루소",
      description: "마블 시네마틱 유니버스의 대단원",
      imageUrl: "",
    },
    {
      id: 4,
      title: "조커",
      year: "2019",
      director: "토드 필립스",
      description: "조커의 소중한 삶을 그린 영화",
      imageUrl: "",
    },
    {
      id: 5,
      title: "라라랜드",
      year: "2016",
      director: "대니 보일",
      description: "라라랜드에서 행복한 삶을 꿈꾸는 두 사람",
      imageUrl: "",
    },
    {
      id: 6,
      title: "타이타닉",
      year: "1997",
      director: "제임스 카메론",
      description: "침몰하는 타이타닉호에서 펼쳐지는 비극적 로맨스",
      imageUrl: "",
    },
    {
      id: 7,
      title: "올드보이",
      year: "2003",
      director: "박찬욱",
      description: "15년간 감금된 남자의 복수 이야기",
      imageUrl: "",
    },
    {
      id: 8,
      title: "인터스텔라",
      year: "2014",
      director: "크리스토퍼 놀란",
      description: "인류의 생존을 위한 우주 탐험 서사시",
      imageUrl: "",
    },
    {
      id: 9,
      title: "아바타",
      year: "2009",
      director: "제임스 카메론",
      description: "판도라 행성에서 벌어지는 환상적인 모험",
      imageUrl: "",
    },
    {
      id: 10,
      title: "부산행",
      year: "2016",
      director: "연상호",
      description: "좀비 바이러스가 창궐한 한국을 배경으로 한 스릴러",
      imageUrl: "",
    },
  ];
};

const getMovie = (id) => {
  const movies = [
    {
      id: 1,
      title: "인셉션",
      year: 2010,
      director: "크리스토퍼 놀란",
      genres: ["액션", "스릴러", "SF"],
      rating: 8.5,
      description: "꿈과 현실의 경계를 넘나드는 액션 블록버스터",
      overview:
        "꿈과 현실의 경계를 넘나드는 액션 블록버스터. 특수 보안 전문가가 팀원들과 함께 타인의 꿈에 침투하여 생각을 훔치는 미션을 수행한다.",
      cast: [
        { name: "레오나르도 디카프리오", role: "돔 코브" },
        { name: "조셉 고든 레빗", role: "아서" },
        { name: "엘렌 페이지", role: "아리아드네" },
      ],
      myReview: "스토리와 연출 모두 훌륭한 영화! 다시 보고 싶어요.",
      imageUrl: "",
    },
    {
      id: 2,
      title: "기생충",
      year: 2019,
      director: "봉준호",
      genres: ["드라마", "스릴러", "코미디"],
      rating: 8.6,
      description: "계급 사회의 모순을 그린 블랙 코미디",
      overview:
        "전원 백수로 살 길 막막하지만 사이는 좋은 기택 가족. 장남 기우가 명문대생 친구의 소개로 고액 과외 일자리를 얻으면서 벌어지는 이야기.",
      cast: [
        { name: "송강호", role: "기택" },
        { name: "이선균", role: "동익" },
        { name: "조여정", role: "연교" },
      ],
      myReview:
        "한국 영화의 새로운 지평을 연 작품. 사회적 메시지가 강렬했어요.",
      imageUrl: "",
    },
    {
      id: 3,
      title: "어벤져스: 엔드게임",
      year: 2019,
      director: "안소니 루소, 조 루소",
      genres: ["액션", "어드벤처", "SF"],
      rating: 8.4,
      description: "마블 시네마틱 유니버스의 대서사시 완결편",
      overview:
        "타노스의 핑거 스냅으로 절반의 생명체가 사라진 후, 남은 어벤져스들이 우주를 구하기 위한 마지막 전투를 벌이는 이야기.",
      cast: [
        { name: "로버트 다우니 주니어", role: "토니 스타크/아이언맨" },
        { name: "크리스 에반스", role: "스티브 로저스/캡틴 아메리카" },
        { name: "스칼렛 요한슨", role: "나타샤 로마노프/블랙 위도우" },
      ],
      myReview: "10년간의 마블 여정의 완벽한 마무리. 감동적이었습니다.",
      imageUrl: "",
    },
    {
      id: 4,
      title: "라라랜드",
      year: 2016,
      director: "데미언 셔젤",
      genres: ["로맨스", "뮤지컬", "드라마"],
      rating: 8.0,
      description: "꿈을 향한 두 사람의 아름다운 로맨스",
      overview:
        "재즈 피아니스트와 배우 지망생이 로스앤젤레스에서 만나 사랑에 빠지지만, 각자의 꿈을 위해 선택해야 하는 이야기.",
      cast: [
        { name: "라이언 고슬링", role: "세바스찬" },
        { name: "엠마 스톤", role: "미아" },
        { name: "존 레전드", role: "키스" },
      ],
      myReview: "음악과 영상미가 환상적인 뮤지컬 영화. 여운이 오래 남아요.",
      imageUrl: "",
    },
    {
      id: 5,
      title: "타이타닉",
      year: 1997,
      director: "제임스 카메론",
      genres: ["로맨스", "드라마", "재난"],
      rating: 7.9,
      description: "침몰하는 타이타닉호에서 펼쳐지는 비극적 로맨스",
      overview:
        "1912년 타이타닉호의 처녀 항해에서 서로 다른 계층의 잭과 로즈가 만나 사랑에 빠지지만, 배가 침몰하면서 벌어지는 비극적인 이야기.",
      cast: [
        { name: "레오나르도 디카프리오", role: "잭 도슨" },
        { name: "케이트 윈슬렛", role: "로즈 드위트 부케이터" },
        { name: "빌리 제인", role: "칼 호클리" },
      ],
      myReview: "시대를 초월한 로맨스 영화의 고전. 몇 번을 봐도 감동적이에요.",
      imageUrl: "",
    },
    {
      id: 6,
      title: "올드보이",
      year: 2003,
      director: "박찬욱",
      genres: ["스릴러", "미스터리", "액션"],
      rating: 8.4,
      description: "15년간 감금된 남자의 복수 이야기",
      overview:
        "이유도 모른 채 15년간 감금되었던 오대수가 풀려나 자신을 가둔 자를 찾아 복수하는 과정에서 충격적인 진실을 마주하는 이야기.",
      cast: [
        { name: "최민식", role: "오대수" },
        { name: "유지태", role: "이우진" },
        { name: "강혜정", role: "미도" },
      ],
      myReview:
        "충격적인 반전과 강렬한 연출이 인상적인 작품. 한국 영화의 걸작입니다.",
      imageUrl: "",
    },
    {
      id: 7,
      title: "인터스텔라",
      year: 2014,
      director: "크리스토퍼 놀란",
      genres: ["SF", "드라마", "어드벤처"],
      rating: 8.6,
      description: "인류의 생존을 위한 우주 탐험 서사시",
      overview:
        "지구의 환경이 악화되어 인류가 멸종 위기에 처한 상황에서, 새로운 행성을 찾기 위해 우주로 떠나는 탐험대의 이야기.",
      cast: [
        { name: "매튜 맥커너히", role: "쿠퍼" },
        { name: "앤 해서웨이", role: "브랜드 박사" },
        { name: "제시카 차스테인", role: "머프" },
      ],
      myReview:
        "과학적 상상력과 감동이 어우러진 놀란의 또 다른 걸작. 우주의 웅장함에 압도됩니다.",
      imageUrl: "",
    },
    {
      id: 8,
      title: "아바타",
      year: 2009,
      director: "제임스 카메론",
      genres: ["SF", "액션", "어드벤처"],
      rating: 7.8,
      description: "판도라 행성에서 벌어지는 환상적인 모험",
      overview:
        "2154년, 지구인들이 판도라 행성의 자원을 채굴하려 하자, 현지 종족 나비족과 갈등이 벌어지는 가운데 한 인간이 나비족의 편에 서게 되는 이야기.",
      cast: [
        { name: "샘 워딩턴", role: "제이크 설리" },
        { name: "조 샐다나", role: "네이티리" },
        { name: "시고니 위버", role: "그레이스 박사" },
      ],
      myReview:
        "혁신적인 3D 기술과 아름다운 판도라의 세계가 인상적. 환경 메시지도 의미 있어요.",
      imageUrl: "",
    },
    {
      id: 9,
      title: "부산행",
      year: 2016,
      director: "연상호",
      genres: ["액션", "스릴러", "드라마"],
      rating: 7.6,
      description: "좀비 바이러스가 창궐한 한국을 배경으로 한 스릴러",
      overview:
        "정체불명의 바이러스가 전국으로 확산되면서 KTX를 타고 부산으로 향하는 사람들이 생존을 위해 사투를 벌이는 이야기.",
      cast: [
        { name: "공유", role: "석우" },
        { name: "정유미", role: "성경" },
        { name: "마동석", role: "상화" },
      ],
      myReview:
        "한국형 좀비 영화의 새로운 기준을 제시한 작품. 액션과 감동이 조화롭습니다.",
      imageUrl: "",
    },
    {
      id: 10,
      title: "조커",
      year: 2019,
      director: "토드 필립스",
      genres: ["드라마", "스릴러", "범죄"],
      rating: 8.4,
      description: "광대에서 악역으로 변해가는 한 남자의 이야기",
      overview:
        "고담시의 코미디언 아서 플렉이 사회의 냉대와 무관심 속에서 점차 조커로 변해가는 과정을 그린 심리 스릴러.",
      cast: [
        { name: "호아킨 피닉스", role: "아서 플렉/조커" },
        { name: "로버트 드 니로", role: "머레이 프랭클린" },
        { name: "자지 비츠", role: "소피 듀몬드" },
      ],
      myReview:
        "호아킨 피닉스의 연기가 압도적인 작품. 사회에 대한 날카로운 비판이 인상적이에요.",
      imageUrl: "",
    },
  ];

  return movies.find((movie) => movie.id === parseInt(id));
};

export { getMovies, getMovie };
