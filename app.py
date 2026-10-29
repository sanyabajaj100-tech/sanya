# =====================================================================
#  GRAND STAY HOTEL - BOOKING COST CALCULATOR
#  Built with Python + Streamlit
#  Run with:  streamlit run app.py
# =====================================================================

import streamlit as st                      # Streamlit builds the web page
from datetime import date, timedelta        # date tools for check-in / check-out
import random                               # used to make a booking reference number

# ---------------------------------------------------------------------
# 1. PAGE SETTINGS  (must be the first Streamlit command)
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Grand Stay Hotel | Booking Calculator",
    page_icon="🏨",
    layout="wide",
)

# ---------------------------------------------------------------------
# 2. CUSTOM STYLING (CSS) - gives the page a professional look
#    Streamlit lets us inject small bits of CSS through st.markdown
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Top banner */
    .hero {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 2.2rem 2.2rem;
        border-radius: 18px;
        margin-bottom: 1.6rem;
        border-bottom: 4px solid #c9a227;
    }
    .hero h1 { color: #ffffff; margin: 0; font-size: 2.3rem; letter-spacing: 0.5px; }
    .hero p  { color: #cfe3ea; margin: 0.5rem 0 0 0; font-size: 1.05rem; }
    .hero .gold { color: #c9a227; }

    /* Room information card */
    .room-card {
        border: 1px solid rgba(128,128,128,0.35);
        border-left: 5px solid #c9a227;
        border-radius: 12px;
        padding: 0.9rem 1.2rem;
        background: rgba(128,128,128,0.07);
        margin: 0.4rem 0 1rem 0;
    }
    .room-card b { font-size: 1.1rem; }

    /* Bill (invoice) table */
    .bill { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
    .bill td { padding: 0.55rem 0.2rem; border-bottom: 1px dashed rgba(128,128,128,0.4); }
    .bill td:last-child { text-align: right; white-space: nowrap; }
    .bill .disc td { color: #2e9e5b; }
    .bill .sub td { font-weight: 600; border-bottom: 1px solid rgba(128,128,128,0.6); }
    .bill .total td {
        font-size: 1.3rem; font-weight: 800; color: #c9a227;
        border-top: 2px solid #c9a227; border-bottom: none; padding-top: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# 3. HOTEL DATA  (stored in dictionaries, lists and tuples)
# ---------------------------------------------------------------------

# Dictionary: room name -> details (price per room per night, max guests per room)
rooms = {
    "Standard Room":      {"rate": 2500,  "capacity": 2, "icon": "🛏️", "desc": "Cosy room with city view, free Wi-Fi and a work desk."},
    "Deluxe Room":        {"rate": 4500,  "capacity": 3, "icon": "🌆", "desc": "Spacious room with king bed, balcony and mini-bar."},
    "Executive Suite":    {"rate": 7000,  "capacity": 3, "icon": "🥂", "desc": "Separate living area, bathtub and lounge access."},
    "Presidential Suite": {"rate": 12000, "capacity": 4, "icon": "👑", "desc": "Our finest suite with private dining and butler service."},
}

# Dictionary: meal plan -> price per guest per night
meal_plans = {
    "Room Only (no meals)":            0,
    "Breakfast Included":              500,
    "Half Board (Breakfast + Dinner)": 1100,
    "Full Board (All meals)":          1700,
}

# List of tuples: (extra service name, price, is the price charged per guest?)
extras = [
    ("Airport Pickup & Drop", 1200, False),
    ("Spa Session",           1500, True),
    ("Late Check-out (4 PM)", 1000, False),
]

# Dictionary: coupon code -> discount percentage
coupons = {"WELCOME10": 10, "STUDENT15": 15, "FEST20": 20}

# Fixed business rules (constants)
WEEKEND_SURCHARGE = 20      # % extra on Friday and Saturday nights
GST_LIMIT = 7500            # room price per night above which GST is 18%

# ---------------------------------------------------------------------
# 4. HEADER BANNER
# ---------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🏨 Grand Stay <span class="gold">Hotel</span></h1>
        <p>Plan your stay and know your exact total before you book - no hidden charges.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Two columns: left = user inputs, right = live bill
left, right = st.columns([1.1, 1], gap="large")

# =====================================================================
# 5. LEFT COLUMN - USER INPUTS (more than 5 input widgets)
# =====================================================================
with left:
    st.subheader("📝 Your Stay Details")

    # Input 1: guest name (text)
    guest_name = st.text_input("Guest name", placeholder="e.g. Rahul Sharma")

    # Input 2 and 3: check-in date and number of nights
    c1, c2 = st.columns(2)
    with c1:
        check_in = st.date_input("Check-in date", value=date.today(), min_value=date.today())
    with c2:
        nights = st.number_input("Number of nights", min_value=1, max_value=60, value=3, step=1)

    st.subheader("🛏️ Choose Your Room")

    # Input 4: room type
    room_type = st.selectbox("Room type", list(rooms.keys()))
    room = rooms[room_type]                      # pick that room's details from the dictionary
    st.markdown(
        f"""
        <div class="room-card">
            <b>{room['icon']} {room_type}</b> &nbsp;|&nbsp; ₹{room['rate']:,} per night<br>
            {room['desc']}<br>
            <small>Sleeps up to {room['capacity']} guests per room</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Input 5 and 6: number of rooms and guests
    c3, c4 = st.columns(2)
    with c3:
        num_rooms = st.number_input("Number of rooms", min_value=1, max_value=10, value=1, step=1)
    with c4:
        guests = st.number_input("Total guests", min_value=1, max_value=40, value=2, step=1)

    st.subheader("🍽️ Meals & Extras")

    # Input 7: meal plan (radio buttons)
    meal_choice = st.radio("Meal plan", list(meal_plans.keys()))

    # Input 8: extra services (checkboxes created with a loop over the list)
    st.write("Add-on services")
    selected_extras = []                         # will store the extras the guest ticks
    for name, price, per_guest in extras:
        if per_guest:
            label = f"{name}  (+₹{price:,} per guest)"
        else:
            label = f"{name}  (+₹{price:,})"
        if st.checkbox(label, key=name):         # True when the box is ticked
            selected_extras.append((name, price, per_guest))

    # Input 9: coupon code (optional)
    coupon_code = st.text_input("Coupon code (optional)", placeholder="e.g. WELCOME10").strip().upper()
    coupon_percent = 0
    if coupon_code != "":
        if coupon_code in coupons:
            coupon_percent = coupons[coupon_code]
            st.success(f"Coupon applied: {coupon_percent}% off your room charges")
        else:
            st.warning("This coupon code is not valid.")

# =====================================================================
# 6. INPUT VALIDATION (error handling) - the app must never crash
# =====================================================================
errors = []                                      # list of problems found
check_out = None

# Check the date calculation safely with try-except
try:
    check_out = check_in + timedelta(days=int(nights))
except (TypeError, ValueError, OverflowError):
    errors.append("Please select a valid check-in date.")

# Check that the guests can fit into the rooms chosen
max_guests = room["capacity"] * num_rooms
if guests > max_guests:
    errors.append(
        f"{room_type} sleeps {room['capacity']} guests per room. "
        f"For {guests} guests please select more rooms (maximum {max_guests} for {num_rooms} room(s))."
    )
elif guests < num_rooms:
    errors.append("You need at least one guest per room. Please reduce the number of rooms.")

# =====================================================================
# 7. RIGHT COLUMN - CALCULATION AND BILL
# =====================================================================
with right:
    st.subheader("🧾 Your Booking Summary")

    if len(errors) > 0:
        # Show every problem clearly instead of crashing
        for message in errors:
            st.error(message)
    else:
        # ---------- A. ROOM CHARGES (loop through every night) ----------
        rate = room["rate"]
        base_room_cost = rate * nights * num_rooms           # normal price for all nights

        weekend_nights = 0
        weekend_extra = 0.0
        for i in range(int(nights)):
            night_date = check_in + timedelta(days=i)        # date of this particular night
            # weekday(): Monday = 0 ... Friday = 4, Saturday = 5, Sunday = 6
            if night_date.weekday() == 4 or night_date.weekday() == 5:
                weekend_nights += 1
                weekend_extra += rate * num_rooms * WEEKEND_SURCHARGE / 100

        room_total = base_room_cost + weekend_extra

        # ---------- B. DISCOUNTS (if / elif / else) ----------
        # Longer stays get a bigger discount on the room charges
        if nights >= 7:
            long_stay_percent = 15
        elif nights >= 4:
            long_stay_percent = 10
        elif nights >= 2:
            long_stay_percent = 5
        else:
            long_stay_percent = 0

        long_stay_discount = room_total * long_stay_percent / 100
        after_long_stay = room_total - long_stay_discount

        coupon_discount = after_long_stay * coupon_percent / 100   # coupon applied after long-stay discount
        room_net = after_long_stay - coupon_discount

        # ---------- C. MEALS AND EXTRAS ----------
        meal_cost = meal_plans[meal_choice] * guests * nights

        extras_cost = 0
        extras_lines = []                                    # lines to print on the bill
        for name, price, per_guest in selected_extras:
            cost = price * guests if per_guest else price
            extras_cost += cost
            extras_lines.append((name, cost))

        # ---------- D. SUBTOTAL, GST AND FINAL TOTAL ----------
        subtotal = room_net + meal_cost + extras_cost

        # GST depends on the room price per night (after discounts):
        # up to Rs 7,500 -> 5%, above Rs 7,500 -> 18%
        net_rate_per_night = room_net / (nights * num_rooms)
        if net_rate_per_night <= GST_LIMIT:
            gst_percent = 5
        else:
            gst_percent = 18

        gst_amount = subtotal * gst_percent / 100
        grand_total = subtotal + gst_amount
        average_per_night = grand_total / nights

        # ---------- E. TOP METRIC CARDS ----------
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Payable", f"₹{grand_total:,.0f}")
        m2.metric("Nights", f"{int(nights)}")
        m3.metric("Avg. per night", f"₹{average_per_night:,.0f}")

        st.caption(
            f"📅 Check-in: **{check_in.strftime('%d %b %Y')}**  →  "
            f"Check-out: **{check_out.strftime('%d %b %Y')}**   |   "
            f"{num_rooms} room(s), {guests} guest(s)"
        )

        # ---------- F. BUILD THE BILL ROWS ----------
        # Each row is a tuple: (description, amount, css style)
        bill_rows = []
        bill_rows.append((f"{room_type}: ₹{rate:,} × {int(nights)} night(s) × {num_rooms} room(s)", base_room_cost, ""))
        if weekend_nights > 0:
            bill_rows.append((f"Weekend surcharge ({weekend_nights} night(s), +{WEEKEND_SURCHARGE}%)", weekend_extra, ""))
        if long_stay_percent > 0:
            bill_rows.append((f"Long-stay discount ({long_stay_percent}%)", -long_stay_discount, "disc"))
        if coupon_percent > 0:
            bill_rows.append((f"Coupon {coupon_code} ({coupon_percent}%)", -coupon_discount, "disc"))
        if meal_cost > 0:
            bill_rows.append((f"{meal_choice}", meal_cost, ""))
        for name, cost in extras_lines:
            bill_rows.append((name, cost, ""))
        bill_rows.append(("Subtotal", subtotal, "sub"))
        bill_rows.append((f"GST @ {gst_percent}%", gst_amount, ""))
        bill_rows.append(("GRAND TOTAL", grand_total, "total"))

        # Turn the rows into an HTML table using a loop
        table_html = '<table class="bill">'
        for description, amount, style in bill_rows:
            if amount < 0:
                amount_text = f"− ₹{abs(amount):,.2f}"
            else:
                amount_text = f"₹{amount:,.2f}"
            table_html += f'<tr class="{style}"><td>{description}</td><td>{amount_text}</td></tr>'
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

        # ---------- G. EXPLANATION OF THE CALCULATION ----------
        with st.expander("ℹ️ How is this calculated?"):
            st.markdown(
                f"""
                1. **Room charges** = rate × nights × rooms, plus **{WEEKEND_SURCHARGE}%** extra on Friday and Saturday nights.
                2. **Long-stay discount**: 2-3 nights = 5%, 4-6 nights = 10%, 7+ nights = 15%.
                3. **Coupon** (if valid) is applied on the room charges after the long-stay discount.
                4. **Meals** = price per guest × guests × nights. **Extras** are added as shown.
                5. **GST** is charged on the subtotal: **5%** if the room price per night is up to ₹7,500, otherwise **18%**.
                   (Simplified for this project; real hotels may tax food and services differently.)
                """
            )

        # ---------- H. CONFIRM BOOKING AND DOWNLOAD BILL ----------
        st.write("")
        name_ready = guest_name.strip() != ""
        if not name_ready:
            st.info("Enter the guest name to enable booking confirmation.")

        if st.button("✅ Confirm Booking", type="primary", disabled=not name_ready):
            booking_ref = "GS" + str(random.randint(100000, 999999))
            st.balloons()
            st.success(
                f"Thank you, {guest_name.strip()}! Your booking is confirmed. "
                f"Booking reference: **{booking_ref}**"
            )

        # Plain-text version of the bill for download
        bill_text = "GRAND STAY HOTEL - BOOKING ESTIMATE\n"
        bill_text += "=" * 44 + "\n"
        bill_text += f"Guest      : {guest_name.strip() if name_ready else '-'}\n"
        bill_text += f"Check-in   : {check_in.strftime('%d %b %Y')}\n"
        bill_text += f"Check-out  : {check_out.strftime('%d %b %Y')}\n"
        bill_text += "-" * 44 + "\n"
        for description, amount, style in bill_rows:
            bill_text += f"{description:<36}{amount:>10,.2f}\n"
        st.download_button("⬇️ Download Bill (.txt)", bill_text, file_name="hotel_bill.txt")

# ---------------------------------------------------------------------
# 8. FOOTER
# ---------------------------------------------------------------------
st.divider()
st.caption("Grand Stay Hotel • Booking Cost Calculator • Made with Python & Streamlit")
