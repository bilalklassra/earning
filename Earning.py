import streamlit as st
import json
import os
import hashlib
from datetime import datetime
import smtplib
from email.message import EmailMessage
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
        return users[email].get("status", "active") == "active"
    return False

def send_email_notification(to_email, amount):
    msg = EmailMessage()
    msg.set_content(f"Your withdraw request of Rs {amount} has been received and is being processed.")
    msg['Subject'] = 'Withdraw Request Received'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = to_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('your_email@gmail.com', 'your_app_password')
        server.send_message(msg)
        server.quit()
    except:
        print("Email send failed")

# ------------------- UI -------------------

st.set_page_config(page_title="E-Wallet App")
st.title("E-Wallet System")

menu = st.sidebar.selectbox("Menu", ["Signup", "Login"])
users = load_users()

if menu == "Signup":
    st.subheader("Create Account")
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
                "balance": 0,
                "status": "pending"
            }
            save_users(users)
            st.success("Signup successful. Wait for admin approval.")

elif menu == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in users and users[email].get("status") == "blocked":
            st.error("Account is blocked.")
        elif authenticate(email, password):
            st.success(f"Welcome {users[email]['name']}")

            option = st.selectbox("Options", [
                "Check Balance", "Add Money", "Transfer Money", "Withdraw",
                "Withdraw History", "Recharge", "Profile", "Export History"
            ])

            if option == "Check Balance":
                st.info(f"Balance: Rs {users[email]['balance']}")

            elif option == "Add Money":
                method = st.selectbox("Payment Method", ["JazzCash", "EasyPaisa", "Bank Transfer"])
                amount = st.number_input("Amount", min_value=10)

                st.warning("Live JazzCash/EasyPaisa API integration requires approved credentials.")
                if st.button("Confirm Payment"):
                    users[email]['balance'] += amount
                    save_users(users)
                    st.success(f"Rs {amount} added.")

            elif option == "Transfer Money":
                to_email = st.text_input("Receiver Email")
                amount = st.number_input("Transfer Amount", min_value=1)
                if st.button("Transfer"):
                    if to_email not in users:
                        st.warning("Receiver not found.")
                    elif users[email]['balance'] < amount:
                        st.warning("Insufficient funds.")
                    else:
                        users[email]['balance'] -= amount
                        users[to_email]['balance'] += amount
                        save_users(users)
                        st.success("Transfer successful.")

            elif option == "Withdraw":
                withdraw_amount = st.number_input("Withdraw Amount", min_value=100, max_value=10000)
                if st.button("Withdraw Now"):
                    if users[email]['balance'] < withdraw_amount:
                        st.error("Insufficient balance.")
                    else:
                        users[email]['balance'] -= withdraw_amount
                        save_users(users)

                        withdraws = []
                        if os.path.exists("withdraws.json"):
                            with open("withdraws.json", "r") as f:
                                withdraws = json.load(f)

                        withdraws.append({
                            "user": email,
                            "amount": withdraw_amount,
                            "status": "Pending",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                        with open("withdraws.json", "w") as f:
                            json.dump(withdraws, f)

                        send_email_notification(email, withdraw_amount)
                        st.success("Withdraw request sent.")

            elif option == "Withdraw History":
                if os.path.exists("withdraws.json"):
                    with open("withdraws.json", "r") as f:
                        all_data = json.load(f)
                        user_data = [r for r in all_data if r['user'] == email]
                        for r in user_data:
                            st.write(f"Rs {r['amount']} | {r['status']} | {r.get('timestamp')}")

            elif option == "Export History":
                if os.path.exists("withdraws.json"):
                    with open("withdraws.json", "r") as f:
                        data = json.load(f)
                        df = pd.DataFrame([r for r in data if r['user'] == email])
                        if not df.empty:
                            st.download_button("Download Excel", df.to_csv(index=False).encode(), "withdraw_history.csv", "text/csv")

            elif option == "Recharge":
                st.write("Recharge option (dummy).")

            elif option == "Profile":
                user = users[email]
                name = st.text_input("Name", value=user["name"])
                if st.button("Update Profile"):
                    user["name"] = name
                    save_users(users)
                    st.success("Updated.")

# ------------------- Admin Panel -------------------

st.sidebar.markdown("---")
admin_mode = st.sidebar.checkbox("Admin Login")

if admin_mode:
    st.subheader("Admin Panel")
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")

    if st.button("Login as Admin"):
        if admin_user == "admin" and admin_pass == "admin123":
            st.success("Logged in as Admin")

            st.write("Pending Users:")
            for u in users:
                if users[u].get("status") == "pending":
                    st.write(f"{u} | {users[u]['name']}")
                    col1, col2 = st.columns(2)
                    if col1.button(f"Approve {u}", key=f"approve_{u}"):
                        users[u]["status"] = "active"
                        save_users(users)
                        st.success(f"{u} approved.")
                    if col2.button(f"Block {u}", key=f"block_{u}"):
                        users[u]["status"] = "blocked"
                        save_users(users)
                        st.warning(f"{u} blocked."
