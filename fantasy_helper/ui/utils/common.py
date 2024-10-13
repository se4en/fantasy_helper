import streamlit as st


def centrize_header(text: str) -> None:
    """
    Centrize the header text by applying a CSS style to the Markdown content.

    Args:
        text (str): The text to be displayed as the header.

    Returns:
        None
    """
    style = "<style>h2 {text-align: center;}</style>"
    st.markdown(style, unsafe_allow_html=True)
    st.header(text)
