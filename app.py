import streamlit as st

# ページの基本設定
st.set_page_config(page_title="漫画閲覧アプリ", layout="wide")

# 許可されたメールアドレス
ALLOWED_EMAIL = "takaharu3711@gmail.com"

st.title("📚 漫画検索・閲覧アプリ")

# ユーザーログイン状態の確認（簡易認証）
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
else:
    # ログイン成功後の表示
    st.sidebar.write(f"ログイン中: **{st.session_state['user_email']}**")
    if st.sidebar.button("ログアウト"):
        st.session_state["user_email"] = ""
        st.rerun()

    st.success("アクセスが許可されました。これから漫画の検索や閲覧機能をここに追加していきます！")
