import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# ページの基本設定
st.set_page_config(page_title="漫画検索・閲覧アプリ", layout="wide")

# 許可されたメールアドレス
ALLOWED_EMAIL = "takaharu3711@gmail.com"

st.title("📚 漫画検索・閲覧アプリ")

# --- 1. ログイン認証処理 ---
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

if not st.session_state["user_email"]:
    st.subheader("🔒 ログイン")
    email_input = st.text_input("メールアドレスを入力してください:", key="login_email")
    if st.button("ログイン", key="login_btn"):
        if email_input.strip() == ALLOWED_EMAIL:
            st.session_state["user_email"] = email_input
            st.success("ログインに成功しました！")
            st.rerun()
        else:
            st.error("このメールアドレスではアクセスできません。")
    st.stop()

# --- 2. ログイン完了後のメイン画面 ---
st.sidebar.write(f"👤 ログイン中: **{st.session_state['user_email']}**")
if st.sidebar.button("ログアウト", key="logout_btn"):
    st.session_state["user_email"] = ""
    st.rerun()

st.header("🔍 漫画を検索する")

# 検索フォーム
col1, col2 = st.columns([1, 2])
with col1:
    genre = st.selectbox("分類（カテゴリ）:", ["すべて", "少年漫画", "少女漫画", "青年漫画", "女性漫画", "ファンタジー", "異世界", "日常・コメディ"], key="genre_select")
with col2:
    keyword = st.text_input("題名（タイトルの一部）:", placeholder="例: スーパーの裏", key="keyword_input")

search_button = st.button("検索実行", type="primary", key="search_btn")

# Googleカスタム検索 API不要の直接Web検索関数
def search_manga_exact(query):
    # Google検索エンジンを利用して soraraw の個別漫画ページ(manga/...)を直接狙い撃ち
    search_url = f"https://html.duckduckgo.com/html/?q=site:soraraw.net/manga/+{urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        results = []
        links = soup.find_all("a", class_="result__url") or soup.find_all("a", class_="result__a")
        
        for a in links:
            title = a.text.strip()
            href = a.get("href", "")
            
            # 外部リダイレクトURLから実際のURLを抽出
            if "uddg=" in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                if "uddg" in parsed:
                    href = parsed["uddg"][0]
            
            if "soraraw" in href and title:
                # 余計な末尾文字を取り除く
                clean_title = title.replace("raw", "").replace("Soraraw", "").replace("https://", "").replace("soraraw.net/manga/", "").strip()
                clean_title = urllib.parse.unquote(clean_title).replace("-", " ")
                
                # 重複除外
                if not any(r["url"] == href for r in results):
                    results.append({
                        "title": clean_title if clean_title else title,
                        "url": href
                    })
        return results
    except Exception as e:
        st.error(f"検索エラーが発生しました: {e}")
        return []

# 検索実行時
if search_button:
    search_term = keyword.strip()
    if not search_term and genre != "すべて":
        search_term = genre
        
    if not search_term:
        st.warning("題名の一部を入力するか、分類を選択してください。")
    else:
        with st.spinner(f"「{search_term}」を検索中..."):
            manga_list = search_manga_exact(search_term)
            
            if manga_list:
                st.success(f"{len(manga_list)} 件の該当ページが見つかりました！")
                
                for i, manga in enumerate(manga_list):
                    st.markdown(f"### 📖 {manga['title']}")
                    st.markdown(f"[👉 サイトでこの作品を開く・読む]({manga['url']})")
                    st.divider()
            else:
                st.info("該当する作品が見つかりませんでした。キーワードを変更してお試しください。")
