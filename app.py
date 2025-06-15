import streamlit as st
import requests
import locale

# Set locale for BDT formatting (Bangladesh Numbering System)
try:
    locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')  # Try Bangladesh locale for proper grouping
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # fallback to system default

def format_bdt(amount):
    # Custom format for BDT (like 12,34,567.89)
    # Python's locale for India gives similar formatting
    try:
        return locale.format_string("%0.2f", amount, grouping=True)
    except:
        # fallback simple comma separator
        return f"{amount:,.2f}"

# App title
st.title("Danish Salary Tax Calculator")

# Inputs
hours = st.number_input("Enter hours worked", value=0, step=1, format="%d")
minutes = st.number_input("Enter minutes worked", value=0, step=1, max_value=59, format="%d")
hourly_rate = st.number_input("Enter hourly wage (DKK)", value=0.00, step=1.0)

# Convert minutes to decimal hours
total_hours = hours + (minutes / 60)

tax_deduction = 5207.00  # fixed monthly deduction
atp_fixed = 66.00        # fixed ATP

# Calculations
gross_salary = round(total_hours * hourly_rate, 2)

# Deduct ATP but ensure salary after ATP is not negative
salary_after_atp = max(0, gross_salary - atp_fixed)

am_bidrag = round(salary_after_atp * 0.08, 2)

a_skat_base = max(0, salary_after_atp - am_bidrag - tax_deduction)

a_skat = round(a_skat_base * 0.38, 2)

# Total tax cannot exceed gross salary
total_tax = min(gross_salary, round(atp_fixed + am_bidrag + a_skat, 2))

net_salary = round(gross_salary - total_tax, 2)

# Display salary breakdown in DKK
st.subheader("💰 Salary Breakdown (in DKK)")
st.write(f"**Gross Earned:** {gross_salary} DKK")
st.write(f"**Total Tax Paid:** {total_tax} DKK")
st.write(f"– ATP: {atp_fixed} DKK")
st.write(f"– AM-bidrag (8% on salary after ATP): {am_bidrag} DKK")
st.write(f"– A-skat (38%): {a_skat} DKK")
st.write(f"**Net Earned:** {net_salary} DKK")

# Currency selection
currency = st.selectbox("Choose currency to convert to:", ["BDT", "USD", "EUR"], index=0)

# Fetch live exchange rates from CurrencyFreaks API
API_KEY = "50c81616ae69471da10d264e01c474cc"
url = f"https://api.currencyfreaks.com/latest?apikey={API_KEY}&symbols=BDT,DKK,USD,EUR"

dkk_to_target = None
api_error = False
exchange_rate_display = None

try:
    response = requests.get(url)
    data = response.json()
    rates = data.get("rates", {})

    # Rates are relative to USD from the API, e.g. "BDT": 105.0 means 1 USD = 105 BDT
    rate_dkk_to_usd = 1 / float(rates.get("DKK", 0)) if rates.get("DKK") else None
    rate_bdt_to_usd = 1 / float(rates.get("BDT", 0)) if rates.get("BDT") else None
    rate_usd = 1.0
    rate_eur_to_usd = 1 / float(rates.get("EUR", 0)) if rates.get("EUR") else None

    if None in [rate_dkk_to_usd, rate_bdt_to_usd, rate_eur_to_usd]:
        api_error = True
    else:
        if currency == "BDT":
            # Convert 1 DKK to USD, then USD to BDT: DKK->USD * USD->BDT
            dkk_to_target = rate_dkk_to_usd * float(rates.get("BDT"))
        elif currency == "USD":
            dkk_to_target = rate_dkk_to_usd
        elif currency == "EUR":
            dkk_to_target = rate_dkk_to_usd * float(rates.get("EUR"))
        exchange_rate_display = dkk_to_target
except Exception as e:
    api_error = True
    st.error(f"Error fetching exchange rate: {e}")

# Show exchange rate if available
if exchange_rate_display:
    st.write(f"**Current Exchange Rate:** 1 DKK = {exchange_rate_display:.4f} {currency}")

# Manual override if API failed or user wants to enter rate manually
manual_override = st.checkbox("Manually enter exchange rate", value=False)
if api_error or manual_override:
    manual_rate = st.number_input(
        f"Enter DKK to {currency} exchange rate manually:", 
        min_value=0.0, format="%.5f"
    )
    if manual_rate > 0:
        dkk_to_target = manual_rate
        exchange_rate_display = manual_rate
        st.write(f"**Using manual exchange rate:** 1 DKK = {manual_rate:.5f} {currency}")

# Show converted amounts if rate is available
if dkk_to_target:
    gross_converted = gross_salary * dkk_to_target
    net_converted = net_salary * dkk_to_target
    tax_converted = total_tax * dkk_to_target

    st.subheader(f"💵 Converted to {currency}")
    if currency == "BDT":
        st.write(f"Gross Income: {format_bdt(gross_converted)} {currency}")
        st.write(f"Net Income: {format_bdt(net_converted)} {currency}")
        st.write(f"Total Tax Paid: {format_bdt(tax_converted)} {currency}")
    else:
        st.write(f"Gross Income: {gross_converted:.2f} {currency}")
        st.write(f"Net Income: {net_converted:.2f} {currency}")
        st.write(f"Total Tax Paid: {tax_converted:.2f} {currency}")
else:
    st.info("Exchange rate unavailable or not entered. Please try again later or enter manually.")
