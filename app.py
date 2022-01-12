import streamlit as st

from streamlit_google_oauth import google_oauth2_required


@google_oauth2_required
def main():
    user_id = st.session_state.user_id
    user_email = st.session_state.user_email
    st.write(f"You're logged in {user_id}, {user_email}")


main()
