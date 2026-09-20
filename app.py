import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

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

# 多重フォールバック検索関数
def search_manga_robust(query):
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
    }

    # 方法1: Yahoo検索プロキシ
    try:
        encoded_query = urllib.parse.quote(f"site:soraraw.com {query}")
        yahoo_url = f"https://search.yahoo.co.jp/search?p={encoded_query}"
        res = requests.get(yahoo_url, headers=headers, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.find_all("a"):
                href = a.get("href", "")
                title = a.text.strip()
                if "soraraw.com" in href and title and len(title) > 3:
                    if not any(r["url"] == href for r in results):
                        results.append({"title": title, "url": href})
    except Exception:
        pass

    # 方法2: ダイレクト検索 (soraraw.com/?s=query)
    if not results:
        try:
            direct_url = f"https://soraraw.com/?s={urllib.parse.quote(query)}"
            res = requests.get(direct_url, headers=headers, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for article in soup.find_all(["article", "div", "h2"]):
                    a_tag = article.find("a") if hasattr(article, 'find') else None
                    if a_tag and a_tag.get("href"):
                        href = a_tag["href"]
                        title = a_tag.text.strip()
                        if "soraraw.com" in href and title:
                            if not any(r["url"] == href for r in results):
                                results.append({"title": title, "url": href})
        except Exception:
            pass

    return results

# 検索実行時
if search_button:
    search_term = keyword.strip()
    if not search_term and genre != "すべて":
        search_term = genre
        
    if not search_term:
        st.warning("題名の一部を入力するか、分類を選択してください。")
    else:
        with st.spinner(f"「{search_term}」を検索中..."):
            manga_list = search_manga_robust(search_term)
            
            if manga_list:
                st.success(f"{len(manga_list)} 件の該当ページが見つかりました！")
                
                for i, manga in enumerate(manga_list):
                    st.markdown(f"### 📖 {manga['title']}")
                    st.markdown(f"[👉 この作品を開いて読む・一覧を見る]({manga['url']})")
                    st.divider()
            else:
                # 最終フォールバック：直接検索用リンクを生成して提示
                st.info("サーバー直接取得でヒットしなかったため、ダイレクト検索リンクを作成しました：")
                direct_search_link = f"https://soraraw.com/?s={urllib.parse.quote(search_term)}"
                st.markdown(f"👉 **[「{search_term}」の検索結果を soraraw.com で直接ひらく]({direct_search_link})**")
