import asyncio
import os

import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2


async def write_authorization_url(client, redirect_uri):
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["profile", "email"],
        extras_params={"access_type": "offline"},
    )
    return authorization_url


async def write_access_token(client, redirect_uri, code):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(client, token):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def google_oauth2_required(func):
    def wrapper(*args, **kwargs):
        client_id = os.environ["GOOGLE_CLIENT_ID"]
        client_secret = os.environ["GOOGLE_CLIENT_SECRET"]
        redirect_uri = os.environ["REDIRECT_URI"]

        client = GoogleOAuth2(client_id, client_secret)
        authorization_url = asyncio.run(write_authorization_url(client=client, redirect_uri=redirect_uri))

        if "token" not in st.session_state:
            st.session_state.token = None

        if st.session_state.token is None:
            try:
                code = st.experimental_get_query_params()["code"]
            except:
                st.write(
                    f"""<h1>
                    Please login using this <a target="_self"
                    href="{authorization_url}">url</a></h1>""",
                    unsafe_allow_html=True,
                )
            else:
                # Verify token is correct:
                try:
                    token = asyncio.run(write_access_token(client=client, redirect_uri=redirect_uri, code=code))
                except:
                    st.write(
                        f"""<h1>
                        This account is not allowed or page was refreshed.
                        Please try again: <a target="_self"
                        href="{authorization_url}">url</a></h1>""",
                        unsafe_allow_html=True,
                    )
                else:
                    # Check if token has expired:
                    if token.is_expired():
                        if token.is_expired():
                            st.write(
                                f"""<h1>
                            Login session has ended,
                            please <a target="_self" href="{authorization_url}">
                            login</a> again.</h1>
                            """,
                                unsafe_allow_html=True,
                            )
                    else:
                        st.session_state["token"] = token
                        user_id, user_email = asyncio.run(get_email(client=client, token=token["access_token"]))
                        st.session_state.user_id = user_id
                        st.session_state.user_email = user_email
                        func(*args, **kwargs)
        else:
            func(*args, **kwargs)

    return wrapper
