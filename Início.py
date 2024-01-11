import streamlit as st

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.header("Bem-vindo aos painéis de ouvidoria")

st.write("""Estes painéis e relatórios têm como objetivo fornecer informações relevantes sobre os dados de ouvidoria.""")

#