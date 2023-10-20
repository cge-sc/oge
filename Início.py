import streamlit as st

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title("Bem-vindo aos painéis de ouvidoria")

st.write("""
Estes painéis têm como objetivo explicar os dados de ouvidoria.
         """)

#