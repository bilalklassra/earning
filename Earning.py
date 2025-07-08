import streamlit as st
import json
import os
import hashlib

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

st.set_page_config(page_title="E-Wallet App", page_icon="💰")
st.title("💰 E-Wallet System (Streamlit Version)")

menu = st.sidebar.selectbox("Menu", ["Signup", "Login"])
users = load_users()

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
            st.success("Signup successful! Now login.")

elif menu == "Login":
    st.subheader("Login to Your Wallet")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if authenticate(email, password):
            st.success(f"Welcome {users[email]['name']}!")

            # Wallet Dashboard
            option = st.selectbox("Options", ["Check Balance", "Add Money", "Transfer Money"])
            if option == "Check Balance":
                st.info(f"Your current balance: Rs {users[email]['balance']}")

            elif option == "Add Money":
                amount = st.number_input("Enter amount to add", min_value=0)
                if st.button("Add"):
                    users[email]['balance'] += amount
                    save_users(users)
                    st.success(f"Added Rs {amount}. New Balance: Rs {users[email]['balance']}")

            elif option == "Transfer Money":
                to_email = st.text_input("Receiver's Email")
                amount = st.number_input("Amount to transfer", min_value=0)

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
        else:
            st.error("Login failed. Check email or password.")
option = st.selectbox("Options", ["Check Balance", "Add Money", "Transfer Money", "Withdraw"])
option = st.selectbox("Options", ["Check Balance", "Add Money", "Transfer Money", "Withdraw"])

if option == "Check Balance":
    st.info(f"Your balance: Rs {users[email]['balance']}")

elif option == "Add Money":
    # Add money block...

elif option == "Transfer Money":
    # Transfer block...

elif option == "Withdraw":
    withdraw_amount = st.number_input("Enter amount to withdraw", min_value=0)

    if st.button("Withdraw Now"):
        if users[email]['balance'] < withdraw_amount:
            st.error("Insufficient balance.")
        else:
            users[email]['balance'] -= withdraw_amount
            save_users(users)
            st.success(f"Rs {withdraw_amount} withdrawn successfully.")

            withdraws = []
            if os.path.exists("withdraws.json"):
                with open("withdraws.json", "r") as f:
                    withdraws = json.load(f)

            withdraws.append({
                "user": email,
                "amount": withdraw_amount,
                "status": "Pending"
            })

            with open("withdraws.json", "w") as f:
                json.dump(withdraws, f)

            st.success("Withdraw request sent. Status: Pending")
elif option == "Withdraw History":
    st.subheader("🧾 Your Withdraw History")
    if os.path.exists("withdraws.json"):
        with open("withdraws.json", "r") as f:
            all_requests = json.load(f)
            user_requests = [r for r in all_requests if r['user'] == email]

            for req in user_requests:
                st.write(f"Amount: Rs {req['amount']} | Status: {req['status']}")
    else:
        st.info("No withdraw history yet.")
option = st.selectbox("Options", ["Check Balance", "Add Money", "Transfer Money", "Withdraw", "Withdraw History"])
st.sidebar.markdown("---")
admin_mode = st.sidebar.checkbox("👑 Admin Login")

if admin_mode:
    st.subheader("Admin Panel")
    admin_user = st.text_input("Admin Username", key="admin_user")
    admin_pass = st.text_input("Admin Password", type="password", key="admin_pass")

    if st.button("Login as Admin"):
        if admin_user == "admin" and admin_pass == "admin123":
            st.success("Admin logged in.")

            if os.path.exists("withdraws.json"):
                with open("withdraws.json", "r") as f:
                    withdraws = json.load(f)

                for i, req in enumerate(withdraws):
                    if req["status"] == "Pending":
                        st.write(f"Request {i+1}: {req['user']} wants to withdraw Rs {req['amount']}")

                        col1, col2 = st.columns(2)
                        if col1.button(f"✅ Approve {i}", key=f"approve_{i}"):
                            withdraws[i]["status"] = "Approved"
                            with open("withdraws.json", "w") as f:
                                json.dump(withdraws, f)
                            st.success("Approved.")

                        if col2.button(f"❌ Reject {i}", key=f"reject_{i}"):
                            withdraws[i]["status"] = "Rejected"
                            # Also refund money back to user
                            users = load_users()
                            users[req['user']]['balance'] += req['amount']
                            save_users(users)
                            with open("withdraws.json", "w") as f:
                                json.dump(withdraws, f)
                            st.warning("Rejected and amount refunded.")
        else:
            st.error("Admin credentials incorrect.")
# Add at the top of your script
import smtplib
from email.message import EmailMessage

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
send_email_notification(email, withdraw_amount)
MIN_WITHDRAW = 100
MAX_WITHDRAW = 10000

if withdraw_amount < MIN_WITHDRAW or withdraw_amount > MAX_WITHDRAW:
    st.error(f"Withdraw amount must be between Rs {MIN_WITHDRAW} and Rs {MAX_WITHDRAW}")
from datetime import datetime
withdraws.append({
    "user": email,
    "amount": withdraw_amount,
    "status": "Pending",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for req in user_requests:
    st.write(f"Rs {req['amount']} | {req['status']} | {req.get('timestamp', 'N/A')}")
st.write(f"{req['user']} | Rs {req['amount']} | {req.get('timestamp', '')}")
st.subheader("📊 Dashboard Stats")

# Total Users
total_users = len(users)
st.info(f"👥 Total Users: {total_users}")

# Total Balance in system
total_balance = sum(user['balance'] for user in users.values())
st.info(f"💰 Total Wallet Balance: Rs {total_balance}")

# Total Withdraw Requests
if os.path.exists("withdraws.json"):
    with open("withdraws.json", "r") as f:
        withdraws = json.load(f)
    total_requests = len(withdraws)
    pending = sum(1 for w in withdraws if w['status'] == "Pending")
    approved = sum(1 for w in withdraws if w['status'] == "Approved")
    rejected = sum(1 for w in withdraws if w['status'] == "Rejected")

    st.info(f"📦 Total Withdraw Requests: {total_requests}")
    st.success(f"✅ Approved: {approved}")
    st.warning(f"🕒 Pending: {pending}")
    st.error(f"❌ Rejected: {rejected}")
else:
    st.info("No withdraw data found.")
option = st.selectbox("Options", ["Check Balance", "Add Money", "Transfer Money", "Withdraw", "Withdraw History", "Recharge", "Profile"])
elif option == "Recharge":
    st.subheader("📱 Recharge Mobile Balance")
    mobile = st.text_input("Enter Mobile Number")
    operator = st.selectbox("Select Operator", ["Jazz", "Zong", "Telenor", "Ufone"])
    recharge_amount = st.number_input("Recharge Amount", min_value=10, max_value=5000)

    if st.button("Recharge Now"):
        if users[email]['balance'] < recharge_amount:
            st.error("Insufficient balance.")
        elif len(mobile) != 11 or not mobile.isdigit():
            st.error("Enter a valid 11-digit mobile number.")
        else:
            users[email]['balance'] -= recharge_amount
            save_users(users)
            st.success(f"Recharge of Rs {recharge_amount} to {mobile} ({operator}) successful.")
elif option == "Profile":
    st.subheader("👤 Your Profile")
    user_data = users[email]

    new_name = st.text_input("Name", value=user_data["name"])
    new_email = st.text_input("Email", value=email)
    new_password = st.text_input("New Password (leave blank to keep current)", type="password")

    if st.button("Update Profile"):
        users.pop(email)  # Remove old key
        updated_email = new_email if new_email else email

        users[updated_email] = {
            "name": new_name,
            "password": user_data["password"] if not new_password else hash_password(new_password),
            "balance": user_data["balance"]
        }

        save_users(users)
        st.success("Profile updated successfully.")
elif option == "Add Money":
    st.subheader("💵 Add Money to Wallet")

    method = st.selectbox("Select Payment Method", ["JazzCash", "EasyPaisa", "Bank Transfer"])
    amount = st.number_input("Enter Amount to Add", min_value=10, max_value=100000)

    if method == "JazzCash":
        st.info("Send money to this JazzCash number: 0300-XXXXXXX\n\nAfter sending, click confirm.")
    elif method == "EasyPaisa":
        st.info("Send money to this EasyPaisa number: 0345-XXXXXXX\n\nAfter sending, click confirm.")
    else:
        st.info("Bank Account: 1234567890\nBank: HBL\nTitle: Bilal Wallets\n\nSend and confirm.")

    if st.button("Confirm Payment"):
        users[email]['balance'] += amount
        save_users(users)
        st.success(f"Rs {amount} added to your wallet via {method}")
