import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# ページの基本設定
st.set_page_config(page_title="漫画検索・閲覧アプリ", layout="wide")

# 許可されたメールアドレス
ALLOWED_EMAIL = "takaharu3711@gmail.com"

# サイトのベースURL
BASE_URL = "https://soraraw.com/"

st.title("📚 漫画検索・閲覧アプリ")

# --- 1. ログイン認証処理 ---
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

if not st.session_state["user_email"]:
    st.subheader("🔒 ログイン")
    email_input = st.text_input("メールアドレスを入力してください:")
    if st.button("ログイン"):
        if email_input.strip() == ALLOWED_EMAIL:
            st.session_state["user_email"] = email_input
            st.success("ログインに成功しました！")
            st.rerun()
        else:
            st.error("このメールアドレスではアクセスできません。")
    st.stop()

# --- 2. ログイン完了後のメイン画面 ---
st.sidebar.write(f"👤 ログイン中: **{st.session_state['user_email']}**")
if st.sidebar.button("ログアウト"):
    st.session_state["user_email"] = ""
    st.rerun()

st.header("🔍 漫画を検索する")

# 検索フォームの入力（分類と題名の一部）
col1, col2 = st.columns([1, 2])
with col1:
    genre = st.selectbox("分類（カテゴリ）:", ["すべて", "少年漫画", "少女漫画", "青年漫画", "女性漫画", "ファンタジー", "異世界", "日常・コメディ"])
with col2:
    keyword = st.text_input("題名（タイトルの一部）:", placeholder="例: オーバーロード")

search_button = st.button("検索実行", type="primary")

# スクレイピング処理関数
def search_manga(query, genre_filter):
    search_url = f"{BASE_URL}?s={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        results = []
        # 作品要素を取得（サイトの構造に合わせて解析）
        articles = soup.find_all("article") or soup.find_all("div", class_="post")
        
        for article in articles:
            title_tag = article.find("h2") or article.find("h3") or article.find("a")
            if not title_tag:
                continue
            title = title_tag.text.strip()
            
            link_tag = article.find("a")
            link = link_tag["href"] if link_tag and "href" in link_tag.attrs else ""
            
            img_tag = article.find("img")
            img_src = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""
            
            if title and link:
                results.append({
                    "title": title,
                    "url": link,
                    "image": img_src
                })
        return results
    except Exception as e:
        st.error(f"データ取得中にエラーが発生しました: {e}")
        return []

# 検索ボタンが押された時の動作
if search_button:
    if not keyword and genre == "すべて":
        st.warning("題名の一部を入力するか、分類を選択してください。")
    else:
        with st.spinner("soraraw.com から検索中..."):
            search_query = keyword if keyword else genre
            manga_list = search_manga(search_query, genre)
            
            if manga_list:
                st.success(f"{len(manga_list)} 件の作品が見つかりました！")
                
                # 結果をグリッド表示
                cols = st.columns(3)
                for i, manga in enumerate(manga_list):
                    with cols[i % 3]:
                        if manga["image"]:
                            st.image(manga["image"], use_container_width=True)
                        st.subheader(manga["title"])
                        if st.button("作品詳細・話一覧", key=f"btn_{i}"):
                            st.session_state["selected_manga"] = manga
                            st.info(f"「{manga['title']}」を選択しました。次回ステップで話一覧と閲覧機能を作成します！")
            else:
                st.info("該当する作品が見つかりませんでした。別のキーワードでお試しください。")
    st.rerun()

st.header("🔍 漫画を検索する")

# 検索フォームの入力（分類と題名の一部）
col1, col2 = st.columns([1, 2])
with col1:
    genre = st.selectbox("分類（カテゴリ）:", ["すべて", "少年漫画", "少女漫画", "青年漫画", "女性漫画", "ファンタジー", "異世界", "日常・コメディ"])
with col2:
    keyword = st.text_input("題名（タイトルの一部）:", placeholder="例: オーバーロード")

search_button = st.button("検索実行", type="primary")

# スクレイピング処理関数
def search_manga(query, genre_filter):
    search_url = f"{BASE_URL}?s={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        results = []
        # 作品要素を取得（サイトの構造に合わせて解析）
        articles = soup.find_all("article") or soup.find_all("div", class_="post")
        
        for article in articles:
            title_tag = article.find("h2") or article.find("h3") or article.find("a")
            if not title_tag:
                continue
            title = title_tag.text.strip()
            
            link_tag = article.find("a")
            link = link_tag["href"] if link_tag and "href" in link_tag.attrs else ""
            
            img_tag = article.find("img")
            img_src = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""
            
            if title and link:
                results.append({
                    "title": title,
                    "url": link,
                    "image": img_src
                })
        return results
    except Exception as e:
        st.error(f"データ取得中にエラーが発生しました: {e}")
        return []

# 検索ボタンが押された時の動作
if search_button:
    if not keyword and genre == "すべて":
        st.warning("題名の一部を入力するか、分類を選択してください。")
    else:
        with st.spinner("soraraw.com から検索中..."):
            search_query = keyword if keyword else genre
            manga_list = search_manga(search_query, genre)
            
            if manga_list:
                st.success(f"{len(manga_list)} 件の作品が見つかりました！")
                
                # 結果をグリッド表示
                cols = st.columns(3)
                for i, manga in enumerate(manga_list):
                    with cols[i % 3]:
                        if manga["image"]:
                            st.image(manga["image"], use_container_width=True)
                        st.subheader(manga["title"])
                        if st.button("作品詳細・話一覧", key=f"btn_{i}"):
                            st.session_state["selected_manga"] = manga
                            st.info(f"「{manga['title']}」を選択しました。次回ステップで話一覧と閲覧機能を作成します！")
            else:
                st.info("該当する作品が見つかりませんでした。別のキーワードでお試しください。")
