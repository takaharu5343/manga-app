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
    keyword = st.text_input("題名（タイトルの一部）:", placeholder="例: 大罪", key="keyword_input")

search_button = st.button("検索実行", type="primary", key="search_btn")

# Yahoo/Google検索経由でサイト内検索を行う関数（ブロック回避）
def search_manga(query):
    # Yahoo!検索を利用して soraraw.com 内のページを取得
    search_url = f"https://search.yahoo.co.jp/search?p=site:soraraw.com+{urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        results = []
        # Yahoo検索結果の各要素を取得
        items = soup.find_all("div", class_="sw-Card") or soup.find_all("li")
        
        for item in items:
            a_tag = item.find("a")
            if not a_tag:
                continue
            
            title = a_tag.text.strip()
            href = a_tag.get("href", "")
            
            # soraraw.com のページかつノイズを除外
            if "soraraw.com" in href and title and len(title) > 2:
                # 余計なドメイン表記や共通文言を取り除く処理
                clean_title = title.split("-")[0].split("|")[0].strip()
                if clean_title not in [r["title"] for r in results]:
                    results.append({
                        "title": clean_title,
                        "url": href,
                        "image": ""
                    })
        return results
    except Exception as e:
        st.error(f"検索中にエラーが発生しました: {e}")
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
            manga_list = search_manga(search_term)
            
            if manga_list:
                st.success(f"{len(manga_list)} 件の関連ページが見つかりました！")
                
                for i, manga in enumerate(manga_list):
                    with st.expander(f"📖 {manga['title']}"):
                        st.write(f"**URL:** {manga['url']}")
                        if st.button("作品ページを開く", key=f"open_btn_{i}"):
                            st.markdown(f"[👉 サイトで読む]({manga['url']})", unsafe_allow_html=True)
            else:
                st.info("該当する作品が見つかりませんでした。別のキーワード（ひらがな・カタカナ・漢字を変えるなど）でお試しください。")
