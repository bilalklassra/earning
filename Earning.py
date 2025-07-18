import streamlit as st
import json
import os
import hashlib
from datetime import datetime
import pandas as pd

# ------------------- Helper Functions -------------------

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(email, password):
    users = load_users()
    if email in users and users[email]["password"] == hash_password(password):
        return True
    return False

# ------------------- Streamlit UI -------------------

st.set_page_config(page_title="E-Wallet App")
st.title("E-Wallet System")

users = load_users()
menu = st.sidebar.selectbox("Menu", ["Signup", "Login"])

if menu == "Signup":
    st.subheader("Create New Account")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        if email in users:
            st.warning("User already exists.")
        else:
            users[email] = {
                "name": name,
                "password": hash_password(password),
                "balance": 0
            }
            save_users(users)
            st.success("Signup successful! You can now log in.")

elif menu == "Login":
    st.subheader("Login to Your Wallet")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if authenticate(email, password):
            st.success(f"Welcome {users[email]['name']}!")

            option = st.selectbox("Options", ["Check Balance", "Add Money", "Transfer Money", "Withdraw", "Withdraw History", "Recharge", "Profile"])

            if option == "Check Balance":
                st.info(f"Your current balance: Rs {users[email]['balance']}")

            elif option == "Add Money":
                method = st.selectbox("Payment Method", ["JazzCash (Placeholder)", "EasyPaisa (Placeholder)"])
                amount = st.number_input("Amount to add", min_value=10)
                if st.button("Confirm Payment"):
                    users[email]['balance'] += amount
                    save_users(users)
                    st.success(f"Rs {amount} added via {method} (simulated)")

            elif option == "Transfer Money":
                to_email = st.text_input("Receiver's Email")
                amount = st.number_input("Transfer Amount", min_value=1)
                if st.button("Transfer"):
                    if to_email not in users:
                        st.warning("Receiver not found.")
                    elif users[email]['balance'] < amount:
                        st.warning("Insufficient balance.")
                    else:
                        users[email]['balance'] -= amount
                        users[to_email]['balance'] += amount
                        save_users(users)
                        st.success(f"Transferred Rs {amount} to {to_email}")

            elif option == "Withdraw":
                withdraw_amount = st.number_input("Withdraw Amount", min_value=100, max_value=10000)
                if st.button("Withdraw Now"):
                    if users[email]['balance'] < withdraw_amount:
                        st.error("Insufficient balance.")
                    else:
                        users[email]['balance'] -= withdraw_amount
                        save_users(users)

                        history = []
                        if os.path.exists("withdraws.json"):
                            with open("withdraws.json", "r") as f:
                                history = json.load(f)

                        history.append({
                            "user": email,
                            "amount": withdraw_amount,
                            "status": "Pending",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                        with open("withdraws.json", "w") as f:
                            json.dump(history, f)

                        st.success("Withdraw request sent.")

            elif option == "Withdraw History":
                if os.path.exists("withdraws.json"):
                    with open("withdraws.json", "r") as f:
                        all_data = json.load(f)
                    user_data = [d for d in all_data if d['user'] == email]
                    for row in user_data:
                        st.write(f"{row['timestamp']} | Rs {row['amount']} | {row['status']}")

                    if st.button("Export to Excel"):
                        df = pd.DataFrame(user_data)
                        df.to_excel("withdraw_history.xlsx", index=False)
                        with open("withdraw_history.xlsx", "rb") as f:
                            st.download_button("Download Excel", f, "Withdraw_History.xlsx")

            elif option == "Recharge":
                number = st.text_input("Mobile Number")
                op = st.selectbox("Operator", ["Jazz", "Zong", "Telenor"])
                amt = st.number_input("Amount", min_value=10)
                if st.button("Recharge Now"):
                    if users[email]['balance'] < amt:
                        st.error("Not enough balance.")
                    else:
                        users[email]['balance'] -= amt
                        save_users(users)
                        st.success(f"Recharge of Rs {amt} to {number} ({op}) done.")

            elif option == "Profile":
                name = st.text_input("Name", value=users[email]["name"])
                new_pass = st.text_input("New Password", type="password")
                if st.button("Update Profile"):
                    users[email]["name"] = name
                    if new_pass:
                        users[email]["password"] = hash_password(new_pass)
                    save_users(users)
                    st.success("Profile updated.")

        else:
            st.error("Login failed. Check email or password.")
