from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import wikipedia
import tmdbsimple as tmdb


# TMDB
def get_tmdb_overview(title):
    search = tmdb.Search().movie(query=title)
    if not search['results']:
        return ""
    return tmdb.Movies(search['results'][0]['id']).info().get('overview', '')

# wikipedia
def get_wikipedia_content(title, lang="ko"):
    wikipedia.set_lang(lang)
    try:
        return wikipedia.page(title).content
    except:
        return ""

# watcha review crawling
def get_watcha_reviews(title, max_comments=20):
    options = Options()
    options.add_argument("--headless")  # 키면 브라우저가 나오지 않음
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        # -------------------- Step 1: Get content ID --------------------
        driver.get(f"https://pedia.watcha.com/ko-KR/search?query={title}")
        wait = WebDriverWait(driver, 10)

        try:
            link_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/ko-KR/contents/']"))
            )
            href = link_elem.get_attribute("href")
            content_id = href.split("/contents/")[1].split("/")[0]
        except Exception as e:
            print(f"[오류] 콘텐츠 ID 추출 실패: {e}")
            return []

        print(f"[INFO] '{title}' → content ID: {content_id}")

        # -------------------- Step 2: Scroll and collect comments --------------------
        url = f"https://pedia.watcha.com/ko-KR/contents/{content_id}/comments"
        driver.get(url)
        time.sleep(3)

        collected = []
        seen_texts = set()
        scroll_attempts = 0
        max_scrolls = 15

        while len(collected) < max_comments and scroll_attempts < max_scrolls:
            comments = driver.find_elements(By.CSS_SELECTOR, "p.CommentText")

            for el in comments:
                text = el.text.strip()
                if text and "스포일러가 있어요!!보기" not in text and text not in seen_texts:
                    collected.append(text)
                    seen_texts.add(text)

                    if len(collected) >= max_comments:
                        break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
            scroll_attempts += 1

        '''
        print(f"\n 총 {len(collected)}개의 댓글이 수집되었습니다 (스포일러 제외, 스크롤 {scroll_attempts}회):\n")
        for i, comment in enumerate(collected):
            print(f"[{i+1}] {comment}")
        '''

        return collected

    finally:
        driver.quit()

