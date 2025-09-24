import streamlit as st
from utils.community import show_leaderboard, display_badges, trade_journal, community_chat

st.title("BlockVista Terminal")

menu = st.sidebar.selectbox("Select Module", ["Leaderboard", "Badges", "Trade Journal", "Community Chat"])

if menu == "Leaderboard":
    demo_leaderboard = [{"name": "Alice", "score": 1200}, {"name": "Bob", "score": 950}]
    show_leaderboard(demo_leaderboard)
elif menu == "Badges":
    demo_badges = ["Trader", "Analyst", "Early Adopter"]
    display_badges(demo_badges)
elif menu == "Trade Journal":
    demo_trades = [{"date": "2025-09-24", "asset": "BTC", "action": "Buy", "amount": 0.1}]
    trade_journal(demo_trades)
elif menu == "Community Chat":
    demo_messages = [{"user": "Alice", "text": "Welcome to BlockVista!"}, {"user": "Bob", "text": "Hello all!"}]
    community_chat(demo_messages)