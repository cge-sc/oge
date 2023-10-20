import streamlit as st

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title('Sobre')

st.write('Texto sobre os painéis')