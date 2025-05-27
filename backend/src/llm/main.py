from qachat import run_qa_mode
from characterchat import run_character_mode

def main():
    print("대화 모드를 선택하세요:")
    print("1. 영화 정보 대화 (일반 QA, 토론)")
    print("2. 영화 인물 대화 (몰입형 캐릭터)")
    mode = input("선택 (1 또는 2): ").strip()
    if mode == "1":
        run_qa_mode()
    elif mode == "2":
        run_character_mode()
    else:
        print("잘못된 입력입니다.")

if __name__ == "__main__":
    main()