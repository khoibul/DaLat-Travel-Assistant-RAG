import streamlit as st

from firebase_client import sign_up, sign_in

from rag import (
    load_guide_embeddings,
    retrieve_entries,
    generate_answer
)


# -----------------------------------
# 1. Page configuration
# -----------------------------------

st.set_page_config(
    page_title="Da Lat Travel Assistant",
    page_icon="🌲",
    layout="centered"
)


# -----------------------------------
# 2. Initialize session state
# -----------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -----------------------------------
# 3. Application title
# -----------------------------------

st.title("🌲 Da Lat Travel Assistant")
st.caption("Your personal travel guide to Da Lat")


# -----------------------------------
# 4. Authentication page
# -----------------------------------

if st.session_state.user is None:

    st.info("Please sign in to access the travel assistant.")

    signup_tab, signin_tab = st.tabs(["Sign Up", "Sign In"])

    # -----------------------------------
    # Sign Up
    # -----------------------------------

    with signup_tab:

        st.subheader("Create a new account")

        with st.form("signup_form"):

            signup_email = st.text_input(
                "Email address",
                key="signup_email"
            )

            signup_password = st.text_input(
                "Password",
                type="password",
                key="signup_password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="confirm_password"
            )

            signup_button = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if signup_button:

            if not signup_email or not signup_password:
                st.error("Please enter your email and password.")

            elif signup_password != confirm_password:
                st.error("Passwords do not match.")

            elif len(signup_password) < 6:
                st.error("Password must contain at least 6 characters.")

            else:
                try:
                    result = sign_up(
                        signup_email.strip(),
                        signup_password
                    )

                    st.session_state.user = {
                        "uid": result.get("localId"),
                        "email": result.get("email")
                    }

                    st.session_state.chat_history = []

                    st.success("Account created successfully!")
                    st.rerun()

                except (ValueError, ConnectionError) as error:
                    st.error(str(error))


    # -----------------------------------
    # Sign In
    # -----------------------------------

    with signin_tab:

        st.subheader("Welcome back!")

        with st.form("signin_form"):

            signin_email = st.text_input(
                "Email address",
                key="signin_email"
            )

            signin_password = st.text_input(
                "Password",
                type="password",
                key="signin_password"
            )

            signin_button = st.form_submit_button(
                "Sign In",
                use_container_width=True
            )

        if signin_button:

            if not signin_email or not signin_password:
                st.error("Please enter your email and password.")

            else:
                try:
                    result = sign_in(
                        signin_email.strip(),
                        signin_password
                    )

                    st.session_state.user = {
                        "uid": result.get("localId"),
                        "email": result.get("email")
                    }

                    st.session_state.chat_history = []

                    st.success("Signed in successfully!")
                    st.rerun()

                except (ValueError, ConnectionError) as error:
                    st.error(str(error))


# -----------------------------------
# 5. Signed-in page
# -----------------------------------

else:

    st.success("You are signed in!")

    # Load RAG knowledge base
    try:
        entries, guide_embeddings = load_guide_embeddings()

    except (ConnectionError, RuntimeError, FileNotFoundError) as error:
        st.error(f"Could not load the travel guide: {error}")
        st.stop()

    st.write(
        f"Welcome, **{st.session_state.user['email']}**!"
    )

    st.divider()

    st.subheader("Travel Assistant")

    # -----------------------------------
    # RAG Chat Interface
    # -----------------------------------

    st.write(
        "Ask me anything about Da Lat!"
    )

    # Display previous conversations
    for chat in st.session_state.chat_history:

        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):
            st.write(chat["answer"])

            with st.expander("View retrieved knowledge"):

                for item in chat["retrieved_results"]:

                    entry = item["entry"]
                    score = item["score"]

                    st.markdown(
                        f"**[{entry['id']}] {entry['title']}**"
                    )

                    st.write(entry["text"])

                    st.caption(
                        f"Similarity score: {score:.4f}"
                    )

                    st.divider()

    # Chat input
    question = st.chat_input(
        "Ask a question about Da Lat..."
    )

    if question:

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):

            with st.spinner("Searching the travel guide..."):

                try:
                    retrieved_results = retrieve_entries(
                        question,
                        entries,
                        guide_embeddings
                    )

                    answer = generate_answer(
                        question,
                        retrieved_results
                    )

                    st.write(answer)

                    with st.expander("View retrieved knowledge"):

                        for item in retrieved_results:

                            entry = item["entry"]
                            score = item["score"]

                            st.markdown(
                                f"**[{entry['id']}] {entry['title']}**"
                            )

                            st.write(entry["text"])

                            st.caption(
                                f"Similarity score: {score:.4f}"
                            )

                            st.divider()

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "retrieved_results": retrieved_results
                    })

                except (ConnectionError, RuntimeError, ValueError) as error:
                    st.error(f"An error occurred: {error}")

    # -----------------------------------
    # Sign Out
    # -----------------------------------

    if st.button("Sign Out", type="primary"):

        st.session_state.user = None

        # Clear chat history when signing out
        st.session_state.chat_history = []

        st.rerun()
