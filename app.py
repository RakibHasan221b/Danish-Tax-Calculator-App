import streamlit as st
import requests
import locale

st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #1E90FF;  /* Blue background */
    color: white;               /* white text */
    font-weight: bold;
    font-size: 18px;
    border-radius: 6px;
    padding: 10px 25px;
}
div.stButton > button:first-child:hover {
    background-color: #1E90FF;  /* darker blue on hover */
}
</style>
""", unsafe_allow_html=True)

try:
    locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

def format_bdt(amount):
    try:
        return locale.format_string("%0.2f", amount, grouping=True)
    except:
        return f"{amount:,.2f}"

st.markdown("""
<h1 style="
    color: #1E90FF; 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    font-weight: 700; 
    letter-spacing: 4px; 
    text-align: center; 
    margin-bottom: 30px;">
    Min Løn
</h1>
""", unsafe_allow_html=True)

def parse_int_input(value, default=0):
    try:
        ivalue = int(value)
        return ivalue if ivalue >= 0 else default
    except:
        return default

def parse_float_input(value, default=0.0):
    try:
        fvalue = float(value)
        return fvalue if fvalue >= 0 else default
    except:
        return default

# Inputs
hours_input = st.text_input("Enter Hours Worked", "")
minutes_input = st.text_input("Enter Minutes Worked", "")
hourly_rate_input = st.text_input("Enter Hourly Wage (DKK)", "")
tax_deduction_input = st.text_input("Enter Personal Tax Deduction Amount", "")
tip_input = st.text_input("Estimated Tip (Optional)", "")
other_tax_percent_input = st.text_input("Other Taxes (e.g. Church Tax, For 5%, Please Enter 5)", "")


hours = parse_int_input(hours_input)
minutes = parse_int_input(minutes_input)
hourly_rate = parse_float_input(hourly_rate_input)
tax_deduction = parse_float_input(tax_deduction_input, default=0.0)
tip = parse_float_input(tip_input, default=0.0)
other_tax_percent = parse_float_input(other_tax_percent_input, default=0.0)


if minutes > 59:
    st.error("Minutes must be between 0 and 59.")
    minutes = 0

raw_total_hours = hours + (minutes / 60)
total_hours = round(raw_total_hours * 4) / 4

def calculate_atp(hours):
    if hours >= 117:
        return 99.00
    elif 78 <= hours < 117:
        return 66.00
    elif 39 <= hours < 78:
        return 33.00
    else:
        return 0.00

atp_fixed = calculate_atp(raw_total_hours)
base_gross_salary = round(total_hours * hourly_rate, 2)
gross_salary = round(base_gross_salary + tip, 2)
salary_after_atp = max(0, gross_salary - atp_fixed)
am_bidrag = round(salary_after_atp * 0.08)
a_skat_base = max(0, salary_after_atp - am_bidrag - tax_deduction)
a_skat = round(a_skat_base * 0.38)

total_tax = min(gross_salary, round(atp_fixed) + round(am_bidrag) + round(a_skat))
net_salary = round(gross_salary - total_tax, 2)

other_tax_amount = 0
if other_tax_percent_input.strip():
    other_tax_amount = round(net_salary * (other_tax_percent / 100))
    net_salary -= other_tax_amount

def colored_text(amount, color):
    return f'<p style="font-size:24px; font-weight:bold; color:{color}; margin:0;">{amount:,.2f} DKK</p>'

if st.button("Calculate"):
    st.session_state.gross_salary = gross_salary
    st.session_state.total_tax = total_tax + other_tax_amount
    st.session_state.net_salary = net_salary
    st.session_state.atp_fixed = atp_fixed
    st.session_state.am_bidrag = am_bidrag
    st.session_state.a_skat = a_skat
    st.session_state.other_tax_amount = other_tax_amount
    st.session_state.other_tax_percent = other_tax_percent
    st.session_state.base_gross_salary = base_gross_salary

if "gross_salary" in st.session_state:
    st.subheader("💰 Salary Breakdown (in DKK)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Gross Earned")
        st.markdown(colored_text(st.session_state.gross_salary, "#2E86C1"), unsafe_allow_html=True)
    with col2:
        st.markdown("### Total Tax Paid")
        st.markdown(colored_text(st.session_state.total_tax, "#C0392B"), unsafe_allow_html=True)
    with col3:
        st.markdown("### Net Earned")
        st.markdown(colored_text(st.session_state.net_salary, "#27AE60"), unsafe_allow_html=True)

    st.write("---")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.write(f"– ATP: {round(st.session_state.atp_fixed):.0f} DKK")
    with col5:
        st.write(f"– AM-bidrag (8%): {round(st.session_state.am_bidrag):.0f} DKK")
    with col6:
        st.write(f"– A-skat (38%): {round(st.session_state.a_skat):.0f} DKK")

    if st.session_state.other_tax_amount > 0:
        st.write(f"– Other Tax (e.g., Church Tax @ {st.session_state.other_tax_percent}%): {round(st.session_state.other_tax_amount):.0f} DKK")

st.write("---")

show_holiday = st.checkbox("Show Holiday Pay Calculation")
if show_holiday:
    holiday_brutto = round(st.session_state.base_gross_salary * 0.125, 2)
    holiday_am = round(holiday_brutto * 0.08)
    askat_base = holiday_brutto - holiday_am
    holiday_askat = round(askat_base * 0.38)
    holiday_net = round(holiday_brutto - holiday_am - holiday_askat, 2)

    st.subheader("🏖️ Holiday Pay Breakdown (in DKK)")
    st.write(f"Gross Holiday Pay: **{holiday_brutto:.2f} DKK**")
    st.write(f"– AM-bidrag (8%): **{round(holiday_am):.0f} DKK**")
    st.write(f"– A-skat (38%): **{round(holiday_askat):.0f} DKK**")
    st.write(f"🚪 Net Holiday Pay: **{holiday_net:.2f} DKK**")

st.write("---")    

show_total_with_holiday = st.checkbox("Show Total Salary Including Holiday Pay")
if show_total_with_holiday and show_holiday:
    total_gross = round(st.session_state.gross_salary + holiday_brutto, 2)
    total_tax = round(st.session_state.total_tax + holiday_am + holiday_askat, 2)
    total_net = round(st.session_state.net_salary + holiday_net, 2)

    st.subheader("🧾 Total Salary Including Holiday Pay")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Gross + Holiday")
        st.markdown(colored_text(total_gross, "#1F618D"), unsafe_allow_html=True)
    with col2:
        st.markdown("### Total Tax Paid")
        st.markdown(colored_text(total_tax, "#A93226"), unsafe_allow_html=True)
    with col3:
        st.markdown("### Net + Holiday")
        st.markdown(colored_text(total_net, "#239B56"), unsafe_allow_html=True)

st.write("---")

enable_conversion = st.checkbox("Enable Currency Conversion")

if enable_conversion:
    currency = st.selectbox("Choose currency to convert to:", ["Select", "BDT", "USD", "EUR"], index=0)
    include_holiday_in_conversion = st.checkbox("Include Holiday Pay in Currency Conversion")
    if currency != "Select":
        API_KEY = "50c81616ae69471da10d264e01c474cc"
        url = f"https://api.currencyfreaks.com/latest?apikey={API_KEY}&symbols=BDT,DKK,USD,EUR"
        dkk_to_target = None
        api_error = False
        exchange_rate_display = None
        try:
            response = requests.get(url)
            data = response.json()
            rates = data.get("rates", {})
            rate_dkk_to_usd = 1 / float(rates.get("DKK", 0)) if rates.get("DKK") else None
            rate_bdt_to_usd = 1 / float(rates.get("BDT", 0)) if rates.get("BDT") else None
            rate_usd = 1.0
            rate_eur_to_usd = 1 / float(rates.get("EUR", 0)) if rates.get("EUR") else None
            if None in [rate_dkk_to_usd, rate_bdt_to_usd, rate_eur_to_usd]:
                api_error = True
            else:
                if currency == "BDT":
                    dkk_to_target = rate_dkk_to_usd * float(rates.get("BDT"))
                elif currency == "USD":
                    dkk_to_target = rate_dkk_to_usd
                elif currency == "EUR":
                    dkk_to_target = rate_dkk_to_usd * float(rates.get("EUR"))
                exchange_rate_display = dkk_to_target
        except Exception as e:
            api_error = True
            st.error(f"Error fetching exchange rate: {e}")

        manual_override = st.checkbox("Manually enter exchange rate", value=False)
        if api_error or manual_override:
            manual_rate = st.number_input(f"Enter DKK to {currency} exchange rate manually:", min_value=0.0, format="%.5f")
            if manual_rate > 0:
                dkk_to_target = manual_rate
                exchange_rate_display = manual_rate
                st.write(f"**Using manual exchange rate:** 1 DKK = {manual_rate:.5f} {currency}")

        if exchange_rate_display:
            st.write(f"**Current Exchange Rate:** 1 DKK = {exchange_rate_display:.4f} {currency}")

        if dkk_to_target:
            # Holiday breakdown
            holiday_brutto = round(st.session_state.base_gross_salary * 0.125, 2)
            holiday_am = round(holiday_brutto * 0.08)
            askat_base = holiday_brutto - holiday_am
            holiday_askat = round(askat_base * 0.38)
            holiday_net = round(holiday_brutto - holiday_am - holiday_askat, 2)

            if include_holiday_in_conversion:
                gross_converted = (st.session_state.gross_salary + holiday_brutto) * dkk_to_target
                net_converted = (st.session_state.net_salary + holiday_net) * dkk_to_target
                tax_converted = (st.session_state.total_tax + holiday_am + holiday_askat) * dkk_to_target
            else:
                gross_converted = st.session_state.gross_salary * dkk_to_target
                net_converted = st.session_state.net_salary * dkk_to_target
                tax_converted = st.session_state.total_tax * dkk_to_target

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

