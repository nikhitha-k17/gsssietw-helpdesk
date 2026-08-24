"""
College Help Desk — AI Agent Chatbot
Run with: streamlit run app.py
"""

import hashlib
import random
from datetime import datetime

import streamlit as st

from knowledge_base import KNOWLEDGE_BASE, get_categories
from agent import HelpDeskAgent, generate_ticket_id
from extra_data import CANTEEN_MENU, CANTEEN_TIMINGS, RULES_REGULATIONS, APPLICATION_TYPES
import database as db
import auth

# ----------------------------------------------------------------------------
# Database setup — creates tables on first run, starts the 30-day retention
# cleanup thread (idempotent: safe to call on every Streamlit rerun).
# ----------------------------------------------------------------------------
db.init_db()
db.start_cleanup_scheduler()
db.cleanup_expired_records()  # also run once synchronously so a fresh boot is clean

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="GSSSIETW Help Desk",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Design tokens & CSS — campus / registrar aesthetic:
# deep navy + brass/gold accent, serif headings (academic), clean sans body.
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --navy: #1B2A4A;
    --navy-light: #2C4270;
    --brass: #B8892F;
    --brass-light: #D9AE5C;
    --parchment: #F6F3EC;
    --ink: #22262E;
    --teal: #2F6F5E;
    --rose: #A6402F;
}

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 { font-family: 'Fraunces', serif; letter-spacing: -0.01em; }

.stApp {
    background: var(--parchment);
}

/* ---- Header banner ---- */
.hd-banner {
    background: linear-gradient(120deg, var(--navy) 0%, var(--navy-light) 100%);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 22px;
    color: #F6F3EC;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 6px 18px rgba(27,42,74,0.18);
}
.hd-seal {
    width: 58px; height: 58px;
    border-radius: 50%;
    background: var(--brass);
    display: flex; align-items: center; justify-content: center;
    font-size: 28px;
    flex-shrink: 0;
    border: 3px solid var(--brass-light);
}
.hd-banner h1 {
    margin: 0; font-size: 1.65rem; color: #FFFFFF; font-weight: 600;
}
.hd-banner p {
    margin: 4px 0 0 0; color: #D8DEEC; font-size: 0.92rem;
}

/* ---- Category / index cards ---- */
.hd-card {
    background: #FFFFFF;
    border: 1px solid #E7E1D3;
    border-left: 4px solid var(--brass);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(27,42,74,0.05);
}
.hd-card b { color: var(--navy); }

/* ---- Ticket badge ---- */
.hd-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-open { background: #FBE7DC; color: var(--rose); }
.badge-progress { background: #FDF1DA; color: var(--brass); }
.badge-resolved { background: #DFEFE8; color: var(--teal); }
.badge-info { background: #E1E7F2; color: var(--navy); }

/* ---- Chat bubbles ---- */
.stChatMessage { border-radius: 12px; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E7E1D3;
}
section[data-testid="stSidebar"] .hd-seal-mini {
    width: 40px; height: 40px; border-radius: 50%;
    background: var(--navy); color: var(--brass-light);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; margin-bottom: 6px;
}

/* ---- Buttons ---- */
.stButton>button {
    background: var(--navy);
    color: #FFFFFF;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    padding: 0.5rem 1.1rem;
}
.stButton>button:hover {
    background: var(--navy-light);
    color: #FFFFFF;
}

/* ---- Divider label ---- */
.hd-eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.72rem;
    color: var(--brass);
    font-weight: 700;
    margin-bottom: 2px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Session state init
# ----------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm the **GSSSIETW Help Desk Assistant**. "
                "Ask me anything about admissions, fees, exams, hostel, library, "
                "placements, or transport — or use the sidebar to "
                "explore FAQs, raise a ticket, or find a department contact."
            ),
        }
    ]
if "agent" not in st.session_state:
    st.session_state.agent = HelpDeskAgent(KNOWLEDGE_BASE)
if "prefill_ticket_desc" not in st.session_state:
    st.session_state.prefill_ticket_desc = ""
if "prefill_ticket_category" not in st.session_state:
    st.session_state.prefill_ticket_category = None
if "llm_api_key" not in st.session_state:
    st.session_state.llm_api_key = ""
if "nav_override" not in st.session_state:
    st.session_state.nav_override = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "admin_email" not in st.session_state:
    st.session_state.admin_email = None
if "is_agent" not in st.session_state:
    st.session_state.is_agent = False
if "agent_staff_email" not in st.session_state:
    st.session_state.agent_staff_email = None
if "is_student" not in st.session_state:
    st.session_state.is_student = False
if "student_email" not in st.session_state:
    st.session_state.student_email = None
if "student_name" not in st.session_state:
    st.session_state.student_name = None
if "_last_faq_search" not in st.session_state:
    st.session_state._last_faq_search = ""
if "_last_submit_sig" not in st.session_state:
    st.session_state._last_submit_sig = {}

agent: HelpDeskAgent = st.session_state.agent

# Demo staff accounts — fixed email/password pairs, same pattern as before.
# Students authenticate separately via real (database-backed) signup/login —
# see auth.py — and have no way to reach these staff logins.
ADMIN_CREDENTIALS = {
    "admin@gsssietw.edu.in": "Admingsssietw@123",
    "principal@gsssietw.edu.in": "Principalgsssietw@123",
    "helpdesk.head@gsssietw.edu.in": "HelpDeskgsssietw@123",
}

# Agent accounts have narrower permissions than Admin (see 🛎️ Agent Dashboard):
# they can view & resolve Tickets / Lost & Found / Applications / Feedback and
# see a 30-day summary, but cannot see raw student search-query text, FAQ
# search analytics, or manage anything Admin-only.
AGENT_CREDENTIALS = {
    "agent1@gsssietw.edu.in": "Agentgsssietw@123",
    "agent2@gsssietw.edu.in": "Agentgsssietw@123",
}


def _submission_signature(*parts):
    """Fingerprint a form's field values so an accidental double-submit
    (double click, or a stray rerun) doesn't create a duplicate record."""
    raw = "||".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def is_duplicate_submission(form_key, *fingerprint_parts):
    sig = _submission_signature(*fingerprint_parts)
    if st.session_state._last_submit_sig.get(form_key) == sig:
        return True
    st.session_state._last_submit_sig[form_key] = sig
    return False


def log_search(query, category, matched, source="Chat"):
    """Record a student's search/question — persisted to the database so it
    survives across sessions and surfaces in the Admin/Agent Dashboards for
    the current 30-day retention window."""
    db.insert_search_log(query, category, matched, source, student_email=st.session_state.student_email)

DEPARTMENTS = [
    {"dept": "Admissions Office", "contact": "Mr. R. Kulkarni", "email": "admissions@gsss.edu.in",
     "phone": "+91 7259256789", "location": "Reception hall"},
    {"dept": "Accounts / Fees Office", "contact": "Ms. S. Iyer", "email": "accounts@gsss.edu.in",
     "phone": "0821 2472452", "location": "A Block"},
    {"dept": "Examination Cell", "contact": "Lavanya S", "email": "lavanyas@gsss.eduin",
     "phone": "0821-4257304", "location": "  A Block "},
    {"dept": "Central Library", "contact": "Banadeshwar Hiremath", "email": "library@gsss.edu",
     "phone": "+91 80 4111 2220", "location": "Library Building, Ground Floor"},
    {"dept": "Hostel Warden Office", "contact": "Mr. K. Reddy", "email": "hostel@gsss.edu.in",
     "phone": "0821 2581304", "location": "Hostel Block C"},
    {"dept": "Placement Cell", "contact": "Mahadeva Prasad S", "email": "placements@gsss.edu.in",
     "phone": "+91 9482086578", "location": "Academic Block B, Room 2"},
    {"dept": "Transport Office", "contact": "Mr.Naveen Kumar", "email": "transport@gsss.edu",
     "phone": "0821 4257305", "location": "Reception hall"},
    {"dept": "Principal ", "contact": "Dr. Shivakumar M.", "email": "principal@gsss.edu.in",
     "phone": "0821-2977306", "location": "A block"},
    {"dept": "ECE-HOD", "contact": "Dr. Rajendra R. Patil", "email": "hodece@gsss.edu.in",
     "phone": "0821 4257305", "location": "A block , Ground floor"},
    {"dept": "ISE-HOD", "contact": "Dr. Gururaj K S", "email": "hodise@gsss.edu.in",
     "phone": "0821 4257305", "location": "A block , Second floor"},
    {"dept": "CSE-HOD", "contact": "Dr.Raviraj P", "email": "raviraj@gsss.edu.in",
     "phone": "0821-4257304", "location": "A block , First floor"},
    {"dept": "EEE-HOD", "contact": "Dr. G Sreeramulu Mahesh", "email": "hodeee@gsss.edu.in",
     "phone": "+91-9980147498", "location": "A block , Ground floor"},
    {"dept": "CSE(AIML)-HOD", "contact": "Dr. Manjuprasad B", "email": "manjuprasad32@gsss.edu.in",
     "phone": "0821-4257304", "location": "D block , Second floor"},
     {"dept": "CSE(AI&DS)-HOD", "contact": "Dr. Roopashree H.R", "email": "hodaids@gsss.edu.in",
     "phone": "0821-4257304", "location": "D block , Third floor"},
]


NOTICES = [
    {"date": "2026-08-25", "title": "Mid-semester exam timetable released", "tag": "Examinations"},
    {"date": "2026-08-22", "title": "Last date for scholarship applications", "tag": "Fees & Scholarships"},
    {"date": "2026-08-20", "title": "Annual tech fest 'Innovate 2026' registrations open", "tag": "Campus Life"},
    {"date": "2026-08-18", "title": "Library extended hours begin for exam season", "tag": "Library"},
    {"date": "2026-08-15", "title": "Placement drive: TCS, Infosys campus visit next week", "tag": "Placements"},
    {"date": "2026-08-10", "title": "Hostel maintenance — water supply interruption Aug 12, 6-9 AM", "tag": "Hostel"},
]

# ----------------------------------------------------------------------------
# Access control — pages every student must be logged in to reach.
# Admin Dashboard and Agent Dashboard have their own independent staff logins
# and are never gated behind student auth.
# ----------------------------------------------------------------------------
STUDENT_PAGES = [
    "💬 Chat Assistant",
    "❓ Browse FAQs",
    "🎫 Raise a Ticket",
    "📋 My Tickets",
    "🧳 Lost & Found",
    "🍽️ Canteen",
    "📜 Rules & Regulations",
    "📝 Apply Online",
    "📞 Department Directory",
    "📅 Notices & Dates",
    "⚙️ Settings & About",
]
STAFF_PAGES = ["🔐 Admin Dashboard", "🛎️ Agent Dashboard"]
LOGIN_PAGE = "🔑 Student Login / Sign Up"

# ----------------------------------------------------------------------------
# Sidebar — navigation & settings
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="hd-seal-mini">🎓</div>', unsafe_allow_html=True)
    st.markdown("### Help Desk Menu")

    if st.session_state.is_student:
        nav_options = STUDENT_PAGES + STAFF_PAGES
    else:
        # Logged-out students can only reach the login/signup page (and the
        # independently-gated staff logins) — everything else redirects here.
        nav_options = [LOGIN_PAGE] + STAFF_PAGES

    default_index = 0
    if st.session_state.nav_override and st.session_state.nav_override in nav_options:
        default_index = nav_options.index(st.session_state.nav_override)
        st.session_state.nav_override = None

    page = st.radio("Navigate to:", nav_options, index=default_index, label_visibility="collapsed")

    # Defense in depth: even if a stale nav_override or a direct rerun tries
    # to land on a protected page while logged out, force back to login.
    if page in STUDENT_PAGES and not st.session_state.is_student:
        page = LOGIN_PAGE

    st.markdown("---")
    if st.session_state.is_student:
        st.markdown('<div class="hd-eyebrow">Signed in as</div>', unsafe_allow_html=True)
        st.write(f"🧑‍🎓 {st.session_state.student_name or st.session_state.student_email}")
        if st.button("Logout", key="student_logout", use_container_width=True):
            st.session_state.is_student = False
            st.session_state.student_email = None
            st.session_state.student_name = None
            st.rerun()

        st.markdown("---")
        st.markdown('<div class="hd-eyebrow">Quick Stats (last 30 days)</div>', unsafe_allow_html=True)
        my_tickets = db.get_tickets(student_email=st.session_state.student_email)
        my_apps = db.get_applications(student_email=st.session_state.student_email)
        open_count = sum(1 for t in my_tickets if t["status"] == "Open")
        st.metric("My Open Tickets", open_count)
        st.metric("My Applications", len(my_apps))
    else:
        st.info("Log in to access student features.")

    st.markdown("---")
    st.caption(" GSSSIETW Help Desk AI Agent · v1.0")

# ----------------------------------------------------------------------------
# Header banner (shown on every page)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hd-banner">
        <div class="hd-seal">🎓</div>
        <div>
            <h1>GSSSIETW Help Desk</h1>
            <p>Your AI-powered assistant for admissions, fees, exams, hostel, and campus services</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# PAGE: Student Login / Sign Up
# ----------------------------------------------------------------------------
if page == LOGIN_PAGE:
    st.markdown('<div class="hd-eyebrow">Student Access</div>', unsafe_allow_html=True)
    st.write("Log in or create your student account to use the Help Desk.")

    tab_login, tab_signup = st.tabs(["🔑 Login", "🆕 Sign Up"])

    with tab_login:
        with st.form("student_login_form"):
            li_email = st.text_input("Email")
            li_password = st.text_input("Password", type="password")
            li_submitted = st.form_submit_button("Login", use_container_width=True)

            if li_submitted:
                record = auth.login_student(li_email, li_password)
                if record:
                    st.session_state.is_student = True
                    st.session_state.student_email = record["email"]
                    st.session_state.student_name = record["name"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    with tab_signup:
        with st.form("student_signup_form", clear_on_submit=True):
            su_name = st.text_input("Full Name")
            su_roll = st.text_input("Roll Number / Student ID")
            su_email = st.text_input("Email")
            su_password = st.text_input("Password (min. 6 characters)", type="password")
            su_confirm = st.text_input("Confirm Password", type="password")
            su_submitted = st.form_submit_button("Create Account", use_container_width=True)

            if su_submitted:
                if su_password != su_confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = auth.signup_student(su_email, su_password, su_name, su_roll)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(msg)

# ----------------------------------------------------------------------------
# PAGE: Chat Assistant
# ----------------------------------------------------------------------------
elif page == "💬 Chat Assistant":
    col_chat, col_side = st.columns([2.4, 1])

    with col_chat:
        st.markdown('<div class="hd-eyebrow">Live Chat</div>', unsafe_allow_html=True)

        chat_container = st.container(height=480)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "🧑‍🎓"):
                    st.markdown(msg["content"])

        user_input = st.chat_input("Type your question... e.g. 'How do I pay my hostel fees?'")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            llm_client = None
            if st.session_state.llm_api_key:
                try:
                    import anthropic
                    llm_client = anthropic.Anthropic(api_key=st.session_state.llm_api_key)
                except Exception:
                    llm_client = None

            result = agent.get_response(user_input, llm_client=llm_client)
            reply_text = result["text"]

            st.session_state.chat_history.append({"role": "assistant", "content": reply_text})
            log_search(user_input, result["category"], result["category"] is not None, source="Chat")

            if result["suggest_ticket"]:
                st.session_state.prefill_ticket_desc = user_input
                st.session_state.prefill_ticket_category = result["category"] or "Other"

            st.rerun()

    with col_side:
        st.markdown('<div class="hd-eyebrow">Try asking about</div>', unsafe_allow_html=True)
        sample_qs = [
            "How do I pay my fees?",
            "What is the library timing?",
            "How do I apply for hostel accommodation?",
            "When is the exam timetable released?",
            "How do I reset my portal password?",
            "What scholarships are available?",
        ]
        for q in sample_qs:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                result = agent.get_response(q)
                st.session_state.chat_history.append({"role": "assistant", "content": result["text"]})
                log_search(q, result["category"], result["category"] is not None, source="Chat")
                if result["suggest_ticket"]:
                    st.session_state.prefill_ticket_desc = q
                    st.session_state.prefill_ticket_category = result["category"] or "Other"
                st.rerun()

        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = [st.session_state.chat_history[0]]
            st.rerun()

        if st.session_state.prefill_ticket_desc:
            st.info("It looks like this needs staff attention.")
            if st.button("🎫 Raise a Ticket for this", use_container_width=True):
                st.session_state.nav_override = "🎫 Raise a Ticket"
                st.rerun()

# ----------------------------------------------------------------------------
# PAGE: Browse FAQs
# ----------------------------------------------------------------------------
elif page == "❓ Browse FAQs":
    st.markdown('<div class="hd-eyebrow">Knowledge Base</div>', unsafe_allow_html=True)
    st.write("Search or browse frequently asked questions by category.")

    search_term = st.text_input("🔍 Search FAQs", placeholder="e.g. revaluation, wifi, curfew...")

    if search_term and st.session_state._last_faq_search != search_term:
        log_search(search_term, None, True, source="FAQ Search")
        st.session_state._last_faq_search = search_term

    categories = get_categories()
    tabs = st.tabs(["All"] + categories)

    def render_faqs(cat_filter):
        any_shown = False
        for category, faqs in KNOWLEDGE_BASE.items():
            if cat_filter != "All" and category != cat_filter:
                continue
            filtered = faqs
            if search_term:
                term = search_term.lower()
                filtered = [
                    f for f in faqs
                    if term in f["question"].lower()
                    or term in f["answer"].lower()
                    or any(term in k.lower() for k in f.get("keywords", []))
                ]
            if not filtered:
                continue
            any_shown = True
            st.markdown(f"#### {category}")
            for item in filtered:
                with st.expander(item["question"]):
                    st.write(item["answer"])
            st.markdown("")
        if not any_shown:
            st.warning("No FAQs match your search. Try a different term or raise a ticket.")

    with tabs[0]:
        render_faqs("All")
    for i, cat in enumerate(categories, start=1):
        with tabs[i]:
            render_faqs(cat)

# ----------------------------------------------------------------------------
# PAGE: Raise a Ticket
# ----------------------------------------------------------------------------
elif page == "🎫 Raise a Ticket":
    st.markdown('<div class="hd-eyebrow">Support Ticket</div>', unsafe_allow_html=True)
    st.write("Can't find your answer? Raise a ticket and our staff will personally follow up.")

    with st.form("ticket_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *", value=st.session_state.student_name or "")
            roll_no = st.text_input("Roll Number / Student ID *")
        with c2:
            email = st.text_input("Email *", value=st.session_state.student_email or "")
            phone = st.text_input("Phone Number")

        category = st.selectbox(
            "Category *",
            get_categories() + ["Other"],
            index=(get_categories() + ["Other"]).index(st.session_state.prefill_ticket_category)
            if st.session_state.prefill_ticket_category in get_categories() + ["Other"]
            else len(get_categories()),
        )
        priority = st.select_slider("Priority", options=["Low", "Medium", "High", "Urgent"], value="Medium")
        description = st.text_area(
            "Describe your issue *",
            value=st.session_state.prefill_ticket_desc,
            height=120,
            placeholder="Please provide as much detail as possible...",
        )

        submitted = st.form_submit_button("Submit Ticket", use_container_width=True)

        if submitted:
            if not name or not roll_no or not email or not description:
                st.error("Please fill in all required fields marked with *.")
            elif is_duplicate_submission("ticket_form", name, roll_no, email, category, description):
                st.warning("Looks like this was already submitted — check **My Tickets** below.")
            else:
                ticket_id = generate_ticket_id()
                db.insert_ticket(
                    ticket_id=ticket_id,
                    student_email=st.session_state.student_email,
                    name=name, roll_no=roll_no, email=email, phone=phone,
                    category=category, priority=priority, description=description,
                )
                st.session_state.prefill_ticket_desc = ""
                st.session_state.prefill_ticket_category = None
                st.success(f"✅ Ticket **{ticket_id}** created successfully! Our team will reach out via email.")
                st.balloons()

# ----------------------------------------------------------------------------
# PAGE: My Tickets
# ----------------------------------------------------------------------------
elif page == "📋 My Tickets":
    st.markdown('<div class="hd-eyebrow">Ticket Tracker</div>', unsafe_allow_html=True)
    st.caption("Showing your tickets from the last 30 days. Status is updated by our Help Desk staff.")

    my_tickets = db.get_tickets(student_email=st.session_state.student_email)

    if not my_tickets:
        st.info("You haven't raised any tickets yet. Head to **Raise a Ticket** to submit one.")
    else:
        f1, f2 = st.columns([1, 1])
        with f1:
            status_filter = st.selectbox("Filter by status", ["All", "Open", "In Progress", "Resolved"])
        with f2:
            cat_filter = st.selectbox("Filter by category", ["All"] + get_categories() + ["Other"])

        for t in my_tickets:
            if status_filter != "All" and t["status"] != status_filter:
                continue
            if cat_filter != "All" and t["category"] != cat_filter:
                continue

            badge_class = {"Open": "badge-open", "In Progress": "badge-progress", "Resolved": "badge-resolved"}[t["status"]]
            st.markdown(
                f"""
                <div class="hd-card">
                    <b>{t['ticket_id']}</b> &nbsp; <span class="hd-badge {badge_class}">{t['status']}</span>
                    &nbsp; <span class="hd-badge badge-progress">{t['priority']} priority</span><br/>
                    <b>Category:</b> {t['category']} &nbsp; | &nbsp; <b>Submitted:</b> {t['created_at']}<br/>
                    <b>By:</b> {t['name']} ({t['roll_no']}) &nbsp; | &nbsp; {t['email']}<br/>
                    <b>Details:</b> {t['description']}
                </div>
                """,
                unsafe_allow_html=True,
            )

# ----------------------------------------------------------------------------
# PAGE: Lost & Found
# ----------------------------------------------------------------------------
elif page == "🧳 Lost & Found":
    st.markdown('<div class="hd-eyebrow">Campus Notice Board</div>', unsafe_allow_html=True)
    st.write("Report something you've **lost** or **found** on campus. Reports appear on the notice board below for everyone to see.")

    tab_board, tab_report = st.tabs(["📋 Notice Board", "➕ Report Lost / Found Item"])

    with tab_report:
        with st.form("lost_found_form", clear_on_submit=True):
            report_type = st.radio("I want to report:", ["Found an item", "Lost an item"], horizontal=True)

            c1, c2 = st.columns(2)
            with c1:
                item_name = st.text_input("Item Name *", placeholder="e.g. Blue Water Bottle, Calculator, ID Card")
                item_category = st.selectbox(
                    "Category",
                    ["Electronics", "Stationery / Books", "ID Cards / Documents", "Bags", "Clothing / Accessories",
                     "Water Bottles / Lunch Boxes", "Keys", "Other"],
                )
            with c2:
                location = st.text_input(
                    "Location *",
                    placeholder="e.g. Library 2nd Floor, Canteen, Bus Stop"
                    if report_type == "Found an item" else "e.g. Last seen near Academic Block A",
                )
                event_date = st.date_input("Date", value=datetime.now())

            description = st.text_area("Description *", placeholder="Color, brand, distinguishing marks, etc.", height=90)
            photo = st.file_uploader("Attach a photo (optional)", type=["png", "jpg", "jpeg"])

            c3, c4 = st.columns(2)
            with c3:
                reporter_name = st.text_input("Your Name *", value=st.session_state.student_name or "")
            with c4:
                contact = st.text_input("Contact (Email / Phone) *", value=st.session_state.student_email or "")

            submitted = st.form_submit_button("Submit Report", use_container_width=True)

            if submitted:
                if not item_name or not location or not description or not reporter_name or not contact:
                    st.error("Please fill in all required fields marked with *.")
                elif is_duplicate_submission(
                    "lost_found_form", report_type, item_name, location, description, reporter_name, contact
                ):
                    st.warning("Looks like this was already submitted — check the **Notice Board** tab.")
                else:
                    report_id = generate_ticket_id("LF")
                    db.insert_lost_found(
                        report_id=report_id,
                        student_email=st.session_state.student_email,
                        item_type="Found" if report_type == "Found an item" else "Lost",
                        item_name=item_name,
                        category=item_category,
                        location=location,
                        event_date=str(event_date),
                        description=description,
                        reporter_name=reporter_name,
                        contact=contact,
                        photo_bytes=photo.getvalue() if photo else None,
                    )
                    item_label = "Found" if report_type == "Found an item" else "Lost"
                    st.success(f"✅ Your **{item_label}** report **{report_id}** has been posted to the notice board!")
                    st.balloons()

    with tab_board:
        board_items = db.get_all_lost_found()

        if not board_items:
            st.info("No reports yet. Be the first to post using the **Report Lost / Found Item** tab.")
        else:
            f1, f2, f3 = st.columns(3)
            with f1:
                type_filter = st.selectbox("Filter by type", ["All", "Found", "Lost"])
            with f2:
                status_filter_lf = st.selectbox("Filter by status", ["All", "Open", "Claimed / Returned"])
            with f3:
                cat_filter_lf = st.selectbox(
                    "Filter by category",
                    ["All", "Electronics", "Stationery / Books", "ID Cards / Documents", "Bags",
                     "Clothing / Accessories", "Water Bottles / Lunch Boxes", "Keys", "Other"],
                )

            for item in board_items:
                if type_filter != "All" and item["type"] != type_filter:
                    continue
                if status_filter_lf == "Open" and item["status"] != "Open":
                    continue
                if status_filter_lf == "Claimed / Returned" and item["status"] == "Open":
                    continue
                if cat_filter_lf != "All" and item["category"] != cat_filter_lf:
                    continue

                type_badge = "badge-resolved" if item["type"] == "Found" else "badge-open"
                status_badge = "badge-progress" if item["status"] == "Open" else "badge-resolved"

                with st.container():
                    st.markdown(
                        f"""
                        <div class="hd-card">
                            <span class="hd-badge {type_badge}">{item['type']}</span>
                            &nbsp; <span class="hd-badge {status_badge}">{item['status']}</span>
                            &nbsp; <span class="hd-badge badge-info">{item['category']}</span>
                            &nbsp; <span style="color:#8A8578; font-size:0.85rem;">{item['report_id']}</span><br/>
                            <b style="font-size:1.05rem;">{item['item_name']}</b><br/>
                            {item['description']}<br/>
                            📍 {item['location']} &nbsp; | &nbsp; 📅 {item['event_date']}<br/>
                            👤 {item['reporter_name']} &nbsp; | &nbsp; 📧 {item['contact']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if item.get("photo"):
                        st.image(item["photo"], width=220)
                    if item["status"] == "Open":
                        if st.button("Mark as Claimed / Returned", key=f"claim_{item['report_id']}"):
                            db.update_lost_found_status(item["report_id"], "Claimed / Returned")
                            st.rerun()

# ----------------------------------------------------------------------------
# PAGE: Canteen
# ----------------------------------------------------------------------------
elif page == "🍽️ Canteen":
    st.markdown('<div class="hd-eyebrow">Mess Timings</div>', unsafe_allow_html=True)
    tcols = st.columns(4)
    for col, (meal, timing) in zip(tcols, CANTEEN_TIMINGS.items()):
        with col:
            st.markdown(
                f"""<div class="hd-card" style="text-align:center;">
                    <b>{meal}</b><br/><span style="color:#8A8578;">{timing}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    tab_menu, tab_feedback = st.tabs(["🍛 Weekly Menu", "⭐ Daily Food Feedback"])

    with tab_menu:
        st.markdown('<div class="hd-eyebrow">This Week\'s Menu</div>', unsafe_allow_html=True)
        today_name = datetime.now().strftime("%A")
        day_choice = st.selectbox(
            "Select a day",
            list(CANTEEN_MENU.keys()),
            index=list(CANTEEN_MENU.keys()).index(today_name) if today_name in CANTEEN_MENU else 0,
        )
        menu = CANTEEN_MENU[day_choice]
        mcols = st.columns(4)
        for col, (meal, items) in zip(mcols, menu.items()):
            with col:
                st.markdown(
                    f"""<div class="hd-card">
                        <div class="hd-eyebrow">{meal}</div>
                        {items}
                    </div>""",
                    unsafe_allow_html=True,
                )

    with tab_feedback:
        st.markdown('<div class="hd-eyebrow">Rate Today\'s Food</div>', unsafe_allow_html=True)
        with st.form("canteen_feedback_form", clear_on_submit=True):
            meal_choice = st.selectbox("Which meal?", ["Breakfast", "Lunch", "Snacks", "Dinner"])
            rating = st.slider("Rating", 1, 5, 4, help="1 = Poor, 5 = Excellent")
            comments = st.text_area("Comments (optional)", placeholder="What did you like or dislike?", height=80)
            name_fb = st.text_input("Your Name (optional, leave blank to stay anonymous)")

            fb_submitted = st.form_submit_button("Submit Feedback", use_container_width=True)
            if fb_submitted:
                final_name = name_fb if name_fb else "Anonymous"
                if is_duplicate_submission("canteen_feedback_form", meal_choice, rating, comments, final_name):
                    st.warning("Looks like this feedback was already submitted — thank you!")
                else:
                    db.insert_feedback(
                        student_email=st.session_state.student_email,
                        date=datetime.now().strftime("%Y-%m-%d"),
                        meal=meal_choice,
                        rating=rating,
                        comments=comments,
                        name=final_name,
                    )
                    st.success("✅ Thanks for your feedback! It helps us improve the mess.")

        all_feedback = db.get_all_feedback()
        if all_feedback:
            st.markdown("---")
            avg_rating = sum(f["rating"] for f in all_feedback) / len(all_feedback)
            st.metric("Average Rating (last 30 days)", f"{avg_rating:.1f} / 5 ⭐")

            st.markdown('<div class="hd-eyebrow">Recent Feedback</div>', unsafe_allow_html=True)
            for f in all_feedback[:10]:
                stars = "⭐" * f["rating"] + "☆" * (5 - f["rating"])
                posted_time = f["created_at"].split(" ")[1] if " " in f["created_at"] else f["created_at"]
                st.markdown(
                    f"""<div class="hd-card">
                        <b>{f['meal']}</b> &nbsp; {stars} &nbsp;
                        <span style="color:#8A8578; font-size:0.85rem;">{f['date']} {posted_time} · {f['name']}</span><br/>
                        {f['comments'] if f['comments'] else '<i>No comments left.</i>'}
                    </div>""",
                    unsafe_allow_html=True,
                )

# ----------------------------------------------------------------------------
# PAGE: Rules & Regulations
# ----------------------------------------------------------------------------
elif page == "📜 Rules & Regulations":
    st.markdown('<div class="hd-eyebrow">Official Policies</div>', unsafe_allow_html=True)
    st.write("Every student is expected to be familiar with and abide by the following rules.")

    search_rules = st.text_input("🔍 Search rules", placeholder="e.g. attendance, ragging, hostel...")

    for category, rules in RULES_REGULATIONS.items():
        filtered_rules = rules
        if search_rules:
            term = search_rules.lower()
            if term not in category.lower():
                filtered_rules = [r for r in rules if term in r.lower()]
        if not filtered_rules:
            continue
        with st.expander(f"📖 {category}", expanded=bool(search_rules)):
            for r in filtered_rules:
                st.markdown(f"- {r}")

# ----------------------------------------------------------------------------
# PAGE: Apply Online (Certificates & ID)
# ----------------------------------------------------------------------------
elif page == "📝 Apply Online":
    st.markdown('<div class="hd-eyebrow">Certificates & ID Services</div>', unsafe_allow_html=True)
    st.write("Apply for a Bonafide Certificate, Transport Certificate, Bus Pass, or ID Card, and track your application status.")

    tab_apply, tab_status = st.tabs(["📝 New Application", "📋 Track My Applications"])

    with tab_apply:
        app_type = st.selectbox("Select Application Type", list(APPLICATION_TYPES.keys()))
        info = APPLICATION_TYPES[app_type]
        st.markdown(
            f"""<div class="hd-card">
                {info['description']}<br/><br/>
                <b>Typical processing time:</b> {info['processing_time']}
            </div>""",
            unsafe_allow_html=True,
        )

        with st.form("application_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                app_name = st.text_input("Full Name *", value=st.session_state.student_name or "")
                app_roll = st.text_input("Roll Number / Student ID *")
                app_program = st.text_input("Program / Branch & Year", placeholder="e.g. B.Tech CSE, 3rd Year")
            with c2:
                app_email = st.text_input("Email *", value=st.session_state.student_email or "")
                app_phone = st.text_input("Phone Number *")

            extra_values = {}
            for field in info["extra_fields"]:
                extra_values[field] = st.text_input(field + " *", key=f"appfield_{app_type}_{field}")

            remarks = st.text_area("Additional Remarks (optional)", height=70)

            app_submitted = st.form_submit_button("Submit Application", use_container_width=True)

            if app_submitted:
                missing = not app_name or not app_roll or not app_email or not app_phone or any(not v for v in extra_values.values())
                if missing:
                    st.error("Please fill in all required fields marked with *.")
                elif is_duplicate_submission(
                    "application_form", app_type, app_name, app_roll, app_email,
                    tuple(sorted(extra_values.items())),
                ):
                    st.warning("Looks like this application was already submitted — check **Track My Applications**.")
                else:
                    app_id = generate_ticket_id("APP")
                    db.insert_application(
                        app_id=app_id,
                        student_email=st.session_state.student_email,
                        app_type=app_type,
                        name=app_name, roll_no=app_roll, program=app_program,
                        email=app_email, phone=app_phone,
                        extra_fields=extra_values, remarks=remarks,
                    )
                    st.success(f"✅ Application **{app_id}** for **{app_type}** submitted! "
                               f"Expected processing time: {info['processing_time']}.")
                    st.balloons()

    with tab_status:
        my_apps = db.get_applications(student_email=st.session_state.student_email)
        st.caption("Showing your applications from the last 30 days.")

        if not my_apps:
            st.info("You haven't submitted any applications yet. Use the **New Application** tab.")
        else:
            status_options = ["All", "Submitted", "Processing", "Ready for Pickup", "Completed"]
            status_filter_app = st.selectbox("Filter by status", status_options)

            badge_map = {
                "Submitted": "badge-open",
                "Processing": "badge-progress",
                "Ready for Pickup": "badge-info",
                "Completed": "badge-resolved",
            }

            for a in my_apps:
                if status_filter_app != "All" and a["status"] != status_filter_app:
                    continue
                extra_str = " · ".join(f"{k}: {v}" for k, v in a["extra"].items())
                st.markdown(
                    f"""<div class="hd-card">
                        <b>{a['app_id']}</b> &nbsp; <span class="hd-badge {badge_map[a['status']]}">{a['status']}</span><br/>
                        <b>{a['type']}</b> &nbsp; | &nbsp; Submitted: {a['created_at']}<br/>
                        By: {a['name']} ({a['roll_no']}) &nbsp; | &nbsp; {a['email']}<br/>
                        {extra_str}
                        {'<br/>Remarks: ' + a['remarks'] if a['remarks'] else ''}
                    </div>""",
                    unsafe_allow_html=True,
                )

# ----------------------------------------------------------------------------
# PAGE: Department Directory
# ----------------------------------------------------------------------------
elif page == "📞 Department Directory":
    st.markdown('<div class="hd-eyebrow">Who to Contact</div>', unsafe_allow_html=True)
    st.write("Reach out directly to a department for specialized help.")

    search = st.text_input("🔍 Search department", placeholder="e.g. hostel, accounts, IT...")

    for d in DEPARTMENTS:
        if search and search.lower() not in d["dept"].lower():
            continue
        st.markdown(
            f"""
            <div class="hd-card">
                <b>{d['dept']}</b><br/>
                Contact: {d['contact']}<br/>
                📧 {d['email']} &nbsp; | &nbsp; 📞 {d['phone']}<br/>
                📍 {d['location']}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------------------------------------------------------------------
# PAGE: Notices & Dates
# ----------------------------------------------------------------------------
elif page == "📅 Notices & Dates":
    st.markdown('<div class="hd-eyebrow">Latest Announcements</div>', unsafe_allow_html=True)

    tag_filter = st.selectbox("Filter by tag", ["All"] + sorted(set(n["tag"] for n in NOTICES)))

    for n in sorted(NOTICES, key=lambda x: x["date"], reverse=True):
        if tag_filter != "All" and n["tag"] != tag_filter:
            continue
        st.markdown(
            f"""
            <div class="hd-card">
                <span class="hd-badge badge-progress">{n['tag']}</span>
                &nbsp; <span style="color:#8A8578; font-size:0.85rem;">{n['date']}</span><br/>
                <b>{n['title']}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------------------------------------------------------------------
# PAGE: Settings & About
# ----------------------------------------------------------------------------
elif page == "⚙️ Settings & About":
    st.markdown('<div class="hd-eyebrow">Configuration</div>', unsafe_allow_html=True)

    st.write(
        "By default, the assistant runs fully offline using a keyword-matching "
        "engine over the built-in knowledge base — no API key required. "
        "Optionally, provide an Anthropic API key below to enable more natural, "
        "conversational responses (Retrieval-Augmented Generation over the same "
        "knowledge base)."
    )
    api_key_input = st.text_input("Anthropic API Key (optional)", type="password", value=st.session_state.llm_api_key)
    if api_key_input != st.session_state.llm_api_key:
        st.session_state.llm_api_key = api_key_input
        st.success("API key updated for this session.")

    st.markdown("---")
    st.markdown('<div class="hd-eyebrow">About this Help Desk</div>', unsafe_allow_html=True)
    st.write(
        """
        **GSSSIETW Help Desk Assistant** is an AI agent built to answer
        common student queries instantly and route anything it can't resolve to
        the right human, via a support ticket.

        **Features:**
        - 💬 Conversational chat assistant with smalltalk + FAQ matching
        - ❓ Searchable FAQ knowledge base across 13 categories
        - 🎫 Ticket raising & tracking system with priority & status
        - 🧳 Lost & Found notice board (report lost/found items, with photos)
        - 🍽️ Canteen weekly menu + daily food feedback
        - 📜 Rules & regulations library
        - 📝 Online applications for certificates, bus pass & ID card
        - 📞 Department directory with direct contacts
        - 📅 Notices & important dates board
        - 🔑 Secure student login (sign up once, log in to use every feature)
        - 🔐 Admin Dashboard — full 30-day analytics, tickets, applications & feedback
        - 🛎️ Agent Dashboard — a lighter staff view for day-to-day ticket handling
        - 🗄️ All student activity is stored for 30 days and automatically deleted after
        - ⚙️ Optional LLM-enhanced responses

        Built with **Streamlit** + a lightweight custom AI agent (`agent.py`) + SQLite (`database.py`).
        """
    )
    st.caption("This is a demo/template application. Replace sample data with your institution's real information before production use.")

# ----------------------------------------------------------------------------
# PAGE: Admin Dashboard
# ----------------------------------------------------------------------------
elif page == "🔐 Admin Dashboard":
    if not st.session_state.is_admin:
        st.markdown('<div class="hd-eyebrow">Staff Login</div>', unsafe_allow_html=True)
        st.write(
            "This area is restricted to authorized college staff. Students do not have "
            "credentials for this login and cannot access the dashboard."
        )
        with st.form("admin_login_form"):
            login_email = st.text_input("Admin Email")
            login_password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login", use_container_width=True)

            if login_submitted:
                if ADMIN_CREDENTIALS.get(login_email) == login_password:
                    st.session_state.is_admin = True
                    st.session_state.admin_email = login_email
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
       

    else:
        colh1, colh2 = st.columns([4, 1])
        with colh1:
            st.markdown(
                f'<div class="hd-eyebrow">Logged in as {st.session_state.admin_email}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"Current 30-day summary (records older than {db.RETENTION_DAYS} days are automatically deleted).")
        with colh2:
            if st.button("Logout", use_container_width=True):
                st.session_state.is_admin = False
                st.session_state.admin_email = None
                st.rerun()

        admin_tabs = st.tabs([
            "📊 Overview", "❓ FAQs", "🎫 Tickets Raised", "🧳 Lost & Found", "📝 Applications Received", "⭐ Feedback Received",
        ])

        summary = db.get_summary_counts()
        all_search_logs = db.get_search_logs()
        all_tickets = db.get_tickets()
        all_lost_found = db.get_all_lost_found()
        all_applications = db.get_applications()
        all_feedback = db.get_all_feedback()

        # ---- Overview ----
        with admin_tabs[0]:
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Student Searches", summary["search_logs"])
            m2.metric("Tickets Raised", summary["tickets"])
            m3.metric("Applications", summary["applications"])
            m4.metric("Feedback Entries", summary["canteen_feedback"])
            m5.metric("Lost & Found Reports", summary["lost_found"])

            st.markdown("---")
            col_cat, col_gap = st.columns([1.2, 1])

            with col_cat:
                st.markdown('<div class="hd-eyebrow">Most Searched Topics</div>', unsafe_allow_html=True)
                cat_counts = db.get_category_counts()
                if not cat_counts:
                    st.info("No student searches logged yet.")
                else:
                    max_count = max(cat_counts.values())
                    for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"**{cat}** — {count}")
                        st.progress(count / max_count)

            with col_gap:
                st.markdown('<div class="hd-eyebrow">Unanswered / Knowledge Gaps</div>', unsafe_allow_html=True)
                unmatched = [l for l in all_search_logs if not l["matched"]][:8]
                if not unmatched:
                    st.success("No unmatched student queries — knowledge base is covering demand well.")
                else:
                    for log in unmatched:
                        st.markdown(
                            f"""<div class="hd-card">
                                <span style="color:#8A8578; font-size:0.8rem;">{log['created_at']} · {log['source']}</span><br/>
                                {log['query']}
                            </div>""",
                            unsafe_allow_html=True,
                        )

            st.markdown("---")
            st.markdown('<div class="hd-eyebrow">Live Search Feed (most recent first)</div>', unsafe_allow_html=True)
            if not all_search_logs:
                st.info("No student activity yet.")
            else:
                for log in all_search_logs[:25]:
                    matched_badge = "badge-resolved" if log["matched"] else "badge-open"
                    who = log["student_email"] or "unknown"
                    st.markdown(
                        f"""<div class="hd-card">
                            <span class="hd-badge badge-info">{log['source']}</span>
                            &nbsp; <span class="hd-badge {matched_badge}">{log['category']}</span>
                            &nbsp; <span style="color:#8A8578; font-size:0.8rem;">{log['created_at']} · {who}</span><br/>
                            {log['query']}
                        </div>""",
                        unsafe_allow_html=True,
                    )

        # ---- FAQs ----
        with admin_tabs[1]:
            st.markdown('<div class="hd-eyebrow">Knowledge Base Contents</div>', unsafe_allow_html=True)
            st.write("Read-only view of every FAQ category and entry, with how often students have searched each topic.")
            cat_counts_faq = db.get_category_counts()

            for category, faqs in KNOWLEDGE_BASE.items():
                searched_count = cat_counts_faq.get(category, 0)
                with st.expander(f"{category}  ·  {len(faqs)} FAQs  ·  searched {searched_count}x"):
                    for item in faqs:
                        st.markdown(f"**Q: {item['question']}**")
                        st.write(item["answer"])
                        st.markdown("")

        # ---- Tickets Raised ----
        with admin_tabs[2]:
            st.markdown('<div class="hd-eyebrow">All Support Tickets</div>', unsafe_allow_html=True)
            if not all_tickets:
                st.info("No tickets have been raised yet.")
            else:
                tf1, tf2 = st.columns(2)
                with tf1:
                    admin_status_filter = st.selectbox("Filter by status", ["All", "Open", "In Progress", "Resolved"], key="admin_ticket_status")
                with tf2:
                    admin_cat_filter = st.selectbox("Filter by category", ["All"] + get_categories() + ["Other"], key="admin_ticket_cat")

                for t in all_tickets:
                    if admin_status_filter != "All" and t["status"] != admin_status_filter:
                        continue
                    if admin_cat_filter != "All" and t["category"] != admin_cat_filter:
                        continue
                    badge_class = {"Open": "badge-open", "In Progress": "badge-progress", "Resolved": "badge-resolved"}[t["status"]]
                    st.markdown(
                        f"""<div class="hd-card">
                            <b>{t['ticket_id']}</b> &nbsp; <span class="hd-badge {badge_class}">{t['status']}</span>
                            &nbsp; <span class="hd-badge badge-progress">{t['priority']} priority</span><br/>
                            <b>Category:</b> {t['category']} &nbsp; | &nbsp; <b>Submitted:</b> {t['created_at']}<br/>
                            <b>By:</b> {t['name']} ({t['roll_no']}) &nbsp; | &nbsp; {t['email']} &nbsp; | &nbsp; {t['phone']}<br/>
                            <b>Details:</b> {t['description']}
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    cA, cB, _ = st.columns([1, 1, 3])
                    with cA:
                        if t["status"] == "Open" and st.button("Mark In Progress", key=f"admin_prog_{t['ticket_id']}"):
                            db.update_ticket_status(t["ticket_id"], "In Progress")
                            st.rerun()
                    with cB:
                        if t["status"] != "Resolved" and st.button("Mark Resolved", key=f"admin_res_{t['ticket_id']}"):
                            db.update_ticket_status(t["ticket_id"], "Resolved")
                            st.rerun()

        # ---- Lost & Found ----
        with admin_tabs[3]:
            st.markdown('<div class="hd-eyebrow">All Lost & Found Reports</div>', unsafe_allow_html=True)
            if not all_lost_found:
                st.info("No Lost & Found reports yet.")
            else:
                lf1, lf2 = st.columns(2)
                with lf1:
                    admin_lf_type = st.selectbox("Filter by type", ["All", "Found", "Lost"], key="admin_lf_type")
                with lf2:
                    admin_lf_status = st.selectbox("Filter by status", ["All", "Open", "Claimed / Returned"], key="admin_lf_status")

                for item in all_lost_found:
                    if admin_lf_type != "All" and item["type"] != admin_lf_type:
                        continue
                    if admin_lf_status != "All" and item["status"] != admin_lf_status:
                        continue
                    type_badge = "badge-resolved" if item["type"] == "Found" else "badge-open"
                    status_badge = "badge-progress" if item["status"] == "Open" else "badge-resolved"
                    st.markdown(
                        f"""<div class="hd-card">
                            <span class="hd-badge {type_badge}">{item['type']}</span>
                            &nbsp; <span class="hd-badge {status_badge}">{item['status']}</span>
                            &nbsp; <span class="hd-badge badge-info">{item['category']}</span>
                            &nbsp; <span style="color:#8A8578; font-size:0.8rem;">{item['report_id']} · {item['created_at']}</span><br/>
                            <b>{item['item_name']}</b> — {item['description']}<br/>
                            📍 {item['location']} &nbsp; | &nbsp; 👤 {item['reporter_name']} ({item['contact']})
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    if item.get("photo"):
                        st.image(item["photo"], width=180)
                    if item["status"] == "Open":
                        if st.button("Mark as Claimed / Returned", key=f"admin_lf_{item['report_id']}"):
                            db.update_lost_found_status(item["report_id"], "Claimed / Returned")
                            st.rerun()

        # ---- Applications Received ----
        with admin_tabs[4]:
            st.markdown('<div class="hd-eyebrow">All Certificate / ID Applications</div>', unsafe_allow_html=True)
            if not all_applications:
                st.info("No applications submitted yet.")
            else:
                admin_app_status = st.selectbox(
                    "Filter by status", ["All", "Submitted", "Processing", "Ready for Pickup", "Completed"], key="admin_app_status"
                )
                stages = ["Submitted", "Processing", "Ready for Pickup", "Completed"]
                badge_map = {"Submitted": "badge-open", "Processing": "badge-progress",
                             "Ready for Pickup": "badge-info", "Completed": "badge-resolved"}

                for a in all_applications:
                    if admin_app_status != "All" and a["status"] != admin_app_status:
                        continue
                    extra_str = " · ".join(f"{k}: {v}" for k, v in a["extra"].items())
                    st.markdown(
                        f"""<div class="hd-card">
                            <b>{a['app_id']}</b> &nbsp; <span class="hd-badge {badge_map[a['status']]}">{a['status']}</span><br/>
                            <b>{a['type']}</b> &nbsp; | &nbsp; Submitted: {a['created_at']}<br/>
                            By: {a['name']} ({a['roll_no']}) &nbsp; | &nbsp; {a['email']} &nbsp; | &nbsp; {a['phone']}<br/>
                            {extra_str}
                            {'<br/>Remarks: ' + a['remarks'] if a['remarks'] else ''}
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    current_idx = stages.index(a["status"])
                    if current_idx < len(stages) - 1:
                        if st.button(f"Advance to '{stages[current_idx + 1]}'", key=f"admin_adv_{a['app_id']}"):
                            db.update_application_status(a["app_id"], stages[current_idx + 1])
                            st.rerun()

        # ---- Feedback Received ----
        with admin_tabs[5]:
            st.markdown('<div class="hd-eyebrow">Canteen Feedback</div>', unsafe_allow_html=True)
            if not all_feedback:
                st.info("No feedback submitted yet.")
            else:
                avg_all = sum(f["rating"] for f in all_feedback) / len(all_feedback)
                st.metric("Overall Average Rating", f"{avg_all:.1f} / 5 ⭐")

                st.markdown('<div class="hd-eyebrow">Average by Meal</div>', unsafe_allow_html=True)
                meal_groups = {}
                for f in all_feedback:
                    meal_groups.setdefault(f["meal"], []).append(f["rating"])
                for meal, ratings in meal_groups.items():
                    avg_meal = sum(ratings) / len(ratings)
                    st.write(f"**{meal}** — {avg_meal:.1f} / 5 ({len(ratings)} responses)")
                    st.progress(avg_meal / 5)

                st.markdown("---")
                st.markdown('<div class="hd-eyebrow">All Feedback</div>', unsafe_allow_html=True)
                for f in all_feedback:
                    stars = "⭐" * f["rating"] + "☆" * (5 - f["rating"])
                    st.markdown(
                        f"""<div class="hd-card">
                            <b>{f['meal']}</b> &nbsp; {stars} &nbsp;
                            <span style="color:#8A8578; font-size:0.85rem;">{f['created_at']} · {f['name']}</span><br/>
                            {f['comments'] if f['comments'] else '<i>No comments left.</i>'}
                        </div>""",
                        unsafe_allow_html=True,
                    )

# ----------------------------------------------------------------------------
# PAGE: Agent Dashboard
# ----------------------------------------------------------------------------
elif page == "🛎️ Agent Dashboard":
    if not st.session_state.is_agent:
        st.markdown('<div class="hd-eyebrow">Staff Login</div>', unsafe_allow_html=True)
        st.write(
            "This area is for Help Desk agents. Agents can view and resolve tickets, Lost & Found "
            "reports, applications, and feedback, with a lighter summary view than the Admin Dashboard. "
            "Students do not have credentials for this login."
        )
        with st.form("agent_login_form"):
            agent_login_email = st.text_input("Agent Email")
            agent_login_password = st.text_input("Password", type="password")
            agent_login_submitted = st.form_submit_button("Login", use_container_width=True)

            if agent_login_submitted:
                if AGENT_CREDENTIALS.get(agent_login_email) == agent_login_password:
                    st.session_state.is_agent = True
                    st.session_state.agent_staff_email = agent_login_email
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
        

    else:
        colh1, colh2 = st.columns([4, 1])
        with colh1:
            st.markdown(
                f'<div class="hd-eyebrow">Logged in as {st.session_state.agent_staff_email}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"Current 30-day summary (records older than {db.RETENTION_DAYS} days are automatically deleted).")
        with colh2:
            if st.button("Logout", use_container_width=True):
                st.session_state.is_agent = False
                st.session_state.agent_staff_email = None
                st.rerun()

        summary = db.get_summary_counts()
        all_tickets = db.get_tickets()
        all_lost_found = db.get_all_lost_found()
        all_applications = db.get_applications()
        all_feedback = db.get_all_feedback()

        agent_tabs = st.tabs([
            "📊 Summary", "🎫 Tickets Raised", "🧳 Lost & Found", "📝 Applications Received", "⭐ Feedback Received",
        ])

        # ---- Summary (aggregate counts only — no raw search-query text; that's Admin-only) ----
        with agent_tabs[0]:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tickets Raised", summary["tickets"])
            m2.metric("Lost & Found Reports", summary["lost_found"])
            m3.metric("Applications", summary["applications"])
            m4.metric("Feedback Entries", summary["canteen_feedback"])

            st.markdown("---")
            st.markdown('<div class="hd-eyebrow">Ticket Status Breakdown</div>', unsafe_allow_html=True)
            ticket_status_counts = db.get_status_counts("tickets")
            if not ticket_status_counts:
                st.info("No tickets in the last 30 days.")
            else:
                for status, count in ticket_status_counts.items():
                    st.write(f"**{status}** — {count}")

            st.markdown('<div class="hd-eyebrow">Application Status Breakdown</div>', unsafe_allow_html=True)
            app_status_counts = db.get_status_counts("applications")
            if not app_status_counts:
                st.info("No applications in the last 30 days.")
            else:
                for status, count in app_status_counts.items():
                    st.write(f"**{status}** — {count}")

            st.caption("Note: detailed student search analytics and FAQ usage stats are only visible in the Admin Dashboard.")

        # ---- Tickets Raised ----
        with agent_tabs[1]:
            st.markdown('<div class="hd-eyebrow">All Support Tickets</div>', unsafe_allow_html=True)
            if not all_tickets:
                st.info("No tickets have been raised yet.")
            else:
                af1, af2 = st.columns(2)
                with af1:
                    agent_status_filter = st.selectbox("Filter by status", ["All", "Open", "In Progress", "Resolved"], key="agent_ticket_status")
                with af2:
                    agent_cat_filter = st.selectbox("Filter by category", ["All"] + get_categories() + ["Other"], key="agent_ticket_cat")

                for t in all_tickets:
                    if agent_status_filter != "All" and t["status"] != agent_status_filter:
                        continue
                    if agent_cat_filter != "All" and t["category"] != agent_cat_filter:
                        continue
                    badge_class = {"Open": "badge-open", "In Progress": "badge-progress", "Resolved": "badge-resolved"}[t["status"]]
                    st.markdown(
                        f"""<div class="hd-card">
                            <b>{t['ticket_id']}</b> &nbsp; <span class="hd-badge {badge_class}">{t['status']}</span>
                            &nbsp; <span class="hd-badge badge-progress">{t['priority']} priority</span><br/>
                            <b>Category:</b> {t['category']} &nbsp; | &nbsp; <b>Submitted:</b> {t['created_at']}<br/>
                            <b>By:</b> {t['name']} ({t['roll_no']}) &nbsp; | &nbsp; {t['email']} &nbsp; | &nbsp; {t['phone']}<br/>
                            <b>Details:</b> {t['description']}
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    cA, cB, _ = st.columns([1, 1, 3])
                    with cA:
                        if t["status"] == "Open" and st.button("Mark In Progress", key=f"agent_prog_{t['ticket_id']}"):
                            db.update_ticket_status(t["ticket_id"], "In Progress")
                            st.rerun()
                    with cB:
                        if t["status"] != "Resolved" and st.button("Mark Resolved", key=f"agent_res_{t['ticket_id']}"):
                            db.update_ticket_status(t["ticket_id"], "Resolved")
                            st.rerun()

        # ---- Lost & Found ----
        with agent_tabs[2]:
            st.markdown('<div class="hd-eyebrow">All Lost & Found Reports</div>', unsafe_allow_html=True)
            if not all_lost_found:
                st.info("No Lost & Found reports yet.")
            else:
                for item in all_lost_found:
                    type_badge = "badge-resolved" if item["type"] == "Found" else "badge-open"
                    status_badge = "badge-progress" if item["status"] == "Open" else "badge-resolved"
                    st.markdown(
                        f"""<div class="hd-card">
                            <span class="hd-badge {type_badge}">{item['type']}</span>
                            &nbsp; <span class="hd-badge {status_badge}">{item['status']}</span>
                            &nbsp; <span class="hd-badge badge-info">{item['category']}</span><br/>
                            <b>{item['item_name']}</b> — {item['description']}<br/>
                            📍 {item['location']} &nbsp; | &nbsp; 👤 {item['reporter_name']} ({item['contact']})
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    if item["status"] == "Open":
                        if st.button("Mark as Claimed / Returned", key=f"agent_lf_{item['report_id']}"):
                            db.update_lost_found_status(item["report_id"], "Claimed / Returned")
                            st.rerun()

        # ---- Applications Received ----
        with agent_tabs[3]:
            st.markdown('<div class="hd-eyebrow">All Certificate / ID Applications</div>', unsafe_allow_html=True)
            if not all_applications:
                st.info("No applications submitted yet.")
            else:
                stages = ["Submitted", "Processing", "Ready for Pickup", "Completed"]
                badge_map = {"Submitted": "badge-open", "Processing": "badge-progress",
                             "Ready for Pickup": "badge-info", "Completed": "badge-resolved"}
                for a in all_applications:
                    extra_str = " · ".join(f"{k}: {v}" for k, v in a["extra"].items())
                    st.markdown(
                        f"""<div class="hd-card">
                            <b>{a['app_id']}</b> &nbsp; <span class="hd-badge {badge_map[a['status']]}">{a['status']}</span><br/>
                            <b>{a['type']}</b> &nbsp; | &nbsp; Submitted: {a['created_at']}<br/>
                            By: {a['name']} ({a['roll_no']}) &nbsp; | &nbsp; {a['email']}<br/>
                            {extra_str}
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    current_idx = stages.index(a["status"])
                    if current_idx < len(stages) - 1:
                        if st.button(f"Advance to '{stages[current_idx + 1]}'", key=f"agent_adv_{a['app_id']}"):
                            db.update_application_status(a["app_id"], stages[current_idx + 1])
                            st.rerun()

        # ---- Feedback Received ----
        with agent_tabs[4]:
            st.markdown('<div class="hd-eyebrow">Canteen Feedback</div>', unsafe_allow_html=True)
            if not all_feedback:
                st.info("No feedback submitted yet.")
            else:
                avg_all = sum(f["rating"] for f in all_feedback) / len(all_feedback)
                st.metric("Overall Average Rating", f"{avg_all:.1f} / 5 ⭐")
                for f in all_feedback:
                    stars = "⭐" * f["rating"] + "☆" * (5 - f["rating"])
                    st.markdown(
                        f"""<div class="hd-card">
                            <b>{f['meal']}</b> &nbsp; {stars} &nbsp;
                            <span style="color:#8A8578; font-size:0.85rem;">{f['created_at']} · {f['name']}</span><br/>
                            {f['comments'] if f['comments'] else '<i>No comments left.</i>'}
                        </div>""",
                        unsafe_allow_html=True,
                    )
