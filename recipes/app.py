import streamlit as st
from streamlit_option_menu import option_menu

# Import other pages
import homepage
import profile

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Recipe App", layout="wide")
    load_css("css/navigation.css")  # Load your CSS file

    # Get query parameters
    query_params = st.query_params

    # Access username using key notation
    username = query_params.get("username")  # or use query_params.username

    if username:  # Check if username exists
        profile.show_profile(username)  # Show profile if username is provided
    else:
        with st.sidebar:
            st.image("logo.png", width=200)
            selection = option_menu(
                menu_title="Navigation",
                options=["Home", "Profile"],
                icons=["house", "person"],
                default_index=0
            )

        if selection == "Home":
            homepage.show_home()
        elif selection == "Profile":
            st.error("Please select a user to view their profile.")  # Handle no username provided

if __name__ == "__main__":
    main()
