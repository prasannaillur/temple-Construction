import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Database setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define Database Models
class Donor(Base):
    __tablename__ = 'donors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    committed_amount = Column(Numeric, nullable=False)
    received_amount = Column(Numeric, default=0)

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    payer = Column(String, nullable=False)
    location = Column(String, nullable=False)
    expected_date = Column(Date, nullable=False)

Base.metadata.create_all(engine)

# Streamlit UI
st.title("Temple Construction Management")

# Donor Management
st.header("Donor Management")
name = st.text_input("Donor Name")
committed = st.number_input("Committed Amount", min_value=0)
if st.button("Add Donor"):
    new_donor = Donor(name=name, committed_amount=committed, received_amount=0)
    session.add(new_donor)
    session.commit()
    st.success("Donor added successfully!")

donors = session.query(Donor).all()
donor_options = {donor.name: donor.id for donor in donors}
donor_name = st.selectbox("Select Donor for Payment", donor_options.keys())
payment = st.number_input("Payment Amount", min_value=0)
if st.button("Add Payment"):
    donor_id = donor_options[donor_name]
    donor = session.query(Donor).filter_by(id=donor_id).first()
    donor.received_amount += payment
    session.commit()
    st.success("Payment recorded successfully!")

donor_df = pd.DataFrame([(d.name, d.committed_amount, d.received_amount) for d in donors], columns=["Name", "Committed Amount", "Received Amount"])
st.dataframe(donor_df)

# Expense Management
st.header("Expense Management")
desc = st.text_input("Expense Description")
amount = st.number_input("Amount", min_value=0)
payer = st.text_input("Payer")
location = st.text_input("Location")
expected_date = st.date_input("Expected Date")
if st.button("Log Expense"):
    new_expense = Expense(description=desc, amount=amount, payer=payer, location=location, expected_date=expected_date)
    session.add(new_expense)
    session.commit()
    st.success("Expense logged successfully!")

expenses = session.query(Expense).all()
expense_df = pd.DataFrame([(e.description, e.amount, e.payer, e.location, e.expected_date) for e in expenses], columns=["Description", "Amount", "Payer", "Location", "Expected Date"])
st.dataframe(expense_df)

# Dashboard
st.header("Dashboard")
total_committed = sum(d.committed_amount for d in donors)
total_received = sum(d.received_amount for d in donors)
total_spent = sum(e.amount for e in expenses)
upcoming_expenses = sum(e.amount for e in expenses if e.expected_date > pd.Timestamp.today().date())

st.metric("Total Committed Donations", f"₹{total_committed}")
st.metric("Total Received Donations", f"₹{total_received}")
st.metric("Total Expenses", f"₹{total_spent}")
st.metric("Upcoming Expenses", f"₹{upcoming_expenses}")
