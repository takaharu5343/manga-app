import streamlit as st
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
    keyword = st.text_input("題名（タイトルの一部）:", placeholder="例: 九条の大罪", key="keyword_input")

search_button = st.button("検索実行", type="primary", key="search_btn")

# 検索実行時
if search_button:
    search_term = keyword.strip()
    if not search_term and genre != "すべて":
        search_term = genre
        
    if not search_term:
        st.warning("題名の一部を入力するか、分類を選択してください。")
    else:
        st.success(f"「{search_term}」の検索リンクを生成しました！")
        
        # soraraw の直接検索URL
        encoded_term = urllib.parse.quote(search_term)
        soraraw_url = f"https://soraraw.net/?s={encoded_term}"
        google_url = f"https://www.google.com/search?q=site:soraraw.net+{encoded_term}"
        
        st.markdown(f"### 📖 「{search_term}」の検索結果を見る")
        
        # 1タップで開くボタン/リンク
        st.link_button("👉 Soraraw で直接検索結果を開く", soraraw_url, type="primary")
        st.link_button("🔍 Google 経由で Soraraw 内を検索", google_url)
        
        st.info("上の「👉 Soraraw で直接検索結果を開く」を押すと、該当作品の一覧ページが直接開きます。")
