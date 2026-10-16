# =========================
# WORKFLOW DATA CLEAN + DASHBOARD
# =========================

import pandas as pd
import numpy as np

# ---------- LOAD ----------
PATH = "/mnt/data/AI_Workflow_Optimization_Dataset_2500_Rows_v1.csv"
df = pd.read_csv(PATH)

# ---------- BASIC CLEANING ----------

# Standardize column names
df.columns = (
    df.columns
    .str.strip()
    .str.replace(" ", "_")
)

# Remove fully duplicated columns (e.g., duplicate Delay_Flag)
df = df.loc[:, ~df.columns.duplicated()]

# Remove duplicate rows
df = df.drop_duplicates()

# ---------- TYPE FIXES ----------

# Datetime parsing
for col in ["Task_Start_Time", "Task_End_Time"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# Numeric columns
num_cols = [
    "Estimated_Time_Minutes",
    "Actual_Time_Minutes",
    "Employee_Workload",
    "Cost_Per_Task"
]

for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Binary Delay_Flag
if "Delay_Flag" in df.columns:
    df["Delay_Flag"] = df["Delay_Flag"].apply(
        lambda x: 1 if str(x).strip() in ["1", "True", "true"] else 0
    )

# ---------- ERROR HANDLING ----------

# Remove impossible durations
if "Actual_Time_Minutes" in df.columns:
    df = df[df["Actual_Time_Minutes"] >= 0]

if "Estimated_Time_Minutes" in df.columns:
    df = df[df["Estimated_Time_Minutes"] >= 0]

# If Delay_Flag missing or wrong, recompute
if set(["Actual_Time_Minutes","Estimated_Time_Minutes"]).issubset(df.columns):
    df["Delay_Flag"] = (
        df["Actual_Time_Minutes"] > df["Estimated_Time_Minutes"]
    ).astype(int)

# Missing values handling
df = df.fillna({
    "Approval_Level": "Unknown",
    "Task_Type": "Unknown",
    "Department": "Unknown"
})

# Numeric NA → median
for col in num_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# ---------- FEATURE ENGINEERING ----------

df["Time_Variance"] = (
    df["Actual_Time_Minutes"] - df["Estimated_Time_Minutes"]
)

df["Cost_per_Minute"] = (
    df["Cost_Per_Task"] / df["Actual_Time_Minutes"].replace(0, np.nan)
)

# ---------- SAVE CLEAN DATA ----------
df.to_csv("/mnt/data/cleaned_workflow_data.csv", index=False)

print("CLEANING COMPLETE")
print(df.info())
print(df.head())

# =========================
# STREAMLIT DASHBOARD
# =========================
# Run with: streamlit run workflow_app.py

import streamlit as st
import plotly.express as px

st.title("Workflow Performance Dashboard")

st.subheader("Dataset Preview")
st.dataframe(df.head(50))

# KPI METRICS
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tasks", len(df))
col2.metric("Avg Actual Time", round(df["Actual_Time_Minutes"].mean(),2))
col3.metric("Delay Rate %",
            round(df["Delay_Flag"].mean()*100,2))
col4.metric("Avg Cost",
            round(df["Cost_Per_Task"].mean(),2))

# ---------- CHARTS ----------

# Tasks by Department
fig1 = px.bar(
    df["Department"].value_counts().reset_index(),
    x="Department",
    y="count",
    title="Tasks by Department"
)
st.plotly_chart(fig1)

# Delay by Priority
fig2 = px.bar(
    df.groupby("Priority_Level")["Delay_Flag"].mean().reset_index(),
    x="Priority_Level",
    y="Delay_Flag",
    title="Delay Rate by Priority"
)
st.plotly_chart(fig2)

# Cost Distribution
fig3 = px.histogram(
    df,
    x="Cost_Per_Task",
    nbins=30,
    title="Cost Distribution"
)
st.plotly_chart(fig3)

# Workload vs Delay
fig4 = px.scatter(
    df,
    x="Employee_Workload",
    y="Actual_Time_Minutes",
    color="Delay_Flag",
    title="Workload vs Actual Time"
)
st.plotly_chart(fig4)

# Process performance
fig5 = px.box(
    df,
    x="Process_Name",
    y="Actual_Time_Minutes",
    title="Process Time Distribution"
)
st.plotly_chart(fig5)
