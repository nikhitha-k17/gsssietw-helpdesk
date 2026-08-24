"""
Knowledge base for the College Help Desk AI Agent.
Organized by category. Each FAQ item has a question, answer, and keywords
used by the agent's matching engine to find the most relevant answer.
"""

KNOWLEDGE_BASE = {
    "Admissions": [
          {
            "question": "How can I get admission?",
            "answer": "Admission is offered according to VTU and Karnataka Government guidelines. Students can apply through the official GSSSIETW admission process.",
            "keywords": ["admission", "apply", "join", "eligibility", "seat"]
        },
        {
            "question": "Is GSSSIETW affiliated to VTU?",
            "answer": "Yes, GSSSIETW is affiliated with Visvesvaraya Technological University (VTU), Belagavi.",
            "keywords": ["VTU", "affiliation", "university"]
        },
        {
            "question": "Is GSSSIETW approved by AICTE?",
            "answer": "Yes, GSSSIETW is approved by AICTE and accredited by NAAC.",
            "keywords": ["AICTE", "approval", "NAAC"]
        },
        {
            "question": "Is GSSSIETW only for girls?",
            "answer": "Yes, GSSSIETW is an exclusive engineering college for women.",
            "keywords": ["girls", "women", "college"]
        },
        {
            "question": "What courses are available for admission?",
            "answer": "The college offers B.E., M.Tech, MBA, and Ph.D. programs.",
            "keywords": ["courses", "B.E.", "M.Tech", "MBA", "Ph.D."]
        },
        {
            "question": "Where is the admission office?",
            "answer": "The admission office is located on the GSSSIETW campus at KRS Road, Metagalli, Mysuru.",
            "keywords": ["admission office", "campus", "Mysuru"]
        },
        {
            "question": "What is the admission process?",
            "answer": "Admissions are done online through the college portal. Steps: 1) Register with email/phone, "
                      "2) Fill the application form, 3) Upload documents (marksheets, ID proof, photo), "
                      "4) Pay the application fee, 5) Attend counselling/entrance test if applicable, "
                      "6) Confirm seat by paying admission fee.",
            "keywords": ["admission", "admissions", "apply", "application", "enroll", "enrollment", "process", "join", "how", "get", "college"]
        },
        {
            "question": "What documents are required for admission?",
            "answer": "You'll need: 10th & 12th marksheets, transfer certificate, migration certificate, "
                      "passport-size photos, ID proof (Aadhar/Passport), category certificate (if applicable), "
                      "and entrance exam scorecard (if applicable).",
            "keywords": ["documents", "required", "admission", "certificate", "marksheet", "papers", "need", "upload"]
        },
        {
            "question": "What is the admission deadline?",
            "answer": "Admission deadlines vary by program. Typically, applications open in May and close by "
                      "mid-July for the upcoming academic year. Please check the official notice board for exact dates.",
            "keywords": ["deadline", "last date", "admission", "when", "date", "close", "apply by"]
        },
        {
            "question": "Is there an entrance exam for admission?",
            "answer": "Some programs (like Engineering and Management) require an entrance exam or merit-based "
                      "selection. Others (like general Arts/Science/Commerce) are admitted based on qualifying "
                      "exam marks. Check your specific program's admission criteria on the college website.",
            "keywords": ["entrance", "exam", "test", "admission", "criteria", "eligibility", "merit"]
        },
    ],
    "Fees & Scholarships": [
         {
            "question": "Are scholarships available?",
            "answer": "Yes, eligible students can apply for scholarships offered by the college and government schemes.",
            "keywords": ["scholarship", "financial aid", "eligible"]
        },
        {
            "question": "What is the Gita Chaitanya Scholarship?",
            "answer": "The Gita Chaitanya Scholarship supports meritorious and economically weaker students.",
            "keywords": ["Gita Chaitanya", "merit", "support"]
        },
        {
            "question": "Is there a merit scholarship?",
            "answer": "Yes, merit-based scholarships are available for eligible students.",
            "keywords": ["merit", "scholarship", "marks"]
        },
        {
            "question": "Where can I get fee details?",
            "answer": "Fee details are available from the college admission office or the official website.",
            "keywords": ["fees", "tuition", "payment"]
        },
        {
            "question": "Can I apply for government scholarships?",
            "answer": "Yes, eligible students can apply for government scholarship schemes through the college.",
            "keywords": ["government", "scholarship", "apply"]
        },
        {
            "question": "Is financial assistance available?",
            "answer": "Yes, financial assistance is available for eligible students through scholarship programs.",
            "keywords": ["financial", "assistance", "aid"]
        },
        {
            "question": "How can I pay my fees?",
            "answer": "Fees can be paid online via the Student Portal using Net Banking, UPI, Debit/Credit Card, "
                      "or offline at the Accounts Office (A Block) via Demand Draft or Cash during "
                      "working hours (9 AM - 4 PM, Mon-Sat).",
            "keywords": ["fees", "fee", "pay", "payment", "tuition", "how", "online", "offline", "money"]
        },
        {
            "question": "What scholarships are available?",
            "answer": "The college offers Merit Scholarships (top 10% scorers), Need-Based Financial Aid, "
                      "Sports Scholarships, and Government Scholarships (SC/ST/OBC/Minority). Applications open "
                      "at the start of each semester on the Scholarship Portal.",
            "keywords": ["scholarship", "scholarships", "financial", "aid", "fee waiver", "merit", "discount"]
        },
        {
            "question": "What happens if I miss the fee payment deadline?",
            "answer": "A late fee penalty of 2% per week applies after the due date. If fees remain unpaid for "
                      "more than 30 days past the deadline, your enrollment may be temporarily suspended. Contact "
                      "the Accounts Office immediately if you need an extension.",
            "keywords": ["late", "fee", "deadline", "miss", "penalty", "due", "overdue", "suspend"]
        },
       
    ],
    "Examinations": [
        
        {
            "question": "How do I apply for revaluation?",
            "answer": "Revaluation applications open within 10 days of result declaration. Apply online through "
                      "the Exam Portal, pay the revaluation fee per subject, and results are typically declared "
                      "within 3-4 weeks.",
            "keywords": ["revaluation", "recheck", "reevaluation", "recount", "marks", "review", "exam"]
        },
        {
            "question": "What is the minimum attendance required to sit for exams?",
            "answer": "As per university norms, a minimum of 75% attendance is required in each subject to be "
                      "eligible to sit for exams. Students below this may need to apply for condonation with "
                      "valid medical/other documentation.",
            "keywords": ["attendance", "minimum", "eligibility", "exam", "percent", "75", "condonation"]
        },
         {
            "question": "Who conducts university examinations?",
            "answer": "VTU conducts university examinations for GSSSIETW students.",
            "keywords": ["VTU", "exam", "university"]
        },
        {
            "question": "Are internal assessments conducted?",
            "answer": "Yes, internal assessments are conducted according to VTU guidelines.",
            "keywords": ["internal", "assessment", "exam"]
        },
        {
            "question": "Where can I check exam updates?",
            "answer": "Exam updates are shared by the college and VTU.",
            "keywords": ["exam", "updates", "notification"]
        },
        {
            "question": "Are practical exams conducted on campus?",
            "answer": "Yes, practical examinations are conducted in college laboratories.",
            "keywords": ["practical", "lab", "exam"]
        },
        {
            "question": "Are semester exams held every term?",
            "answer": "Yes, semester examinations follow the VTU academic schedule.",
            "keywords": ["semester", "exam", "schedule"]
        },
        {
            "question": "How can I know my exam timetable?",
            "answer": "Students should check official college and VTU notifications for exam timetables.",
            "keywords": ["timetable", "exam", "schedule"]
        }
    ],
    "Library": [
         {
            "question": "Does GSSSIETW have a library?",
            "answer": "Yes, GSSSIETW has a library with academic resources for students.",
            "keywords": ["library", "books", "study"]
        },
        {
            "question": "Can students borrow books?",
            "answer": "Yes, students can borrow books according to library rules.",
            "keywords": ["borrow", "books", "library"]
        },
        {
            "question": "Where is the library located?",
            "answer": "The library is located on the A block on GSSSIETW campus.",
            "keywords": ["library", "location", "campus"]
        },
        {
            "question": "Is there a digital library?",
            "answer": "The library supports digital and academic learning resources.",
            "keywords": ["digital", "library", "resources"]
        },
        {
            "question": "Can students study in the library?",
            "answer": "Yes, students can use the library for academic study.",
            "keywords": ["study", "library", "students"]
        },
        {
            "question": "Does the library support academics?",
            "answer": "Yes, it provides learning resources for academic development.",
            "keywords": ["academic", "library", "learning"]
        },
        {
            "question": "What are the library timings?",
            "answer": "The Library is open  8:00 AM to 7:00 PM ",
                      
            "keywords": ["library", "timing", "timings", "hours", "open", "closed", "when"]
        },
        {
            "question": "How many books can I borrow?",
            "answer": "Undergraduate students can borrow up to 3 books for 14 days, postgraduate students up to "
                      "5 books for 21 days. Books can be renewed once online if not reserved by another student.",
            "keywords": ["books", "borrow", "issue", "library", "how many", "limit", "renew"]
        },
        {
            "question": "What is the fine for late return of library books?",
            "answer": "A fine of ₹1 per day per book is charged for late returns. If a book is lost or damaged, "
                      "you'll need to pay the replacement cost plus a processing fee.",
            "keywords": ["fine", "library", "late", "return", "book", "penalty", "lost", "damaged"]
        },
    ],
    "Hostel & Accommodation": [
        {
            "question": "How do I apply for hostel accommodation?",
            "answer": "Apply through the Hostel Portal after admission confirmation. Submit the hostel fee, "
                      "a medical fitness certificate, and parent's consent form. Allotment is based on distance "
                      "from home and availability, on a first-come-first-served basis.",
            "keywords": ["hostel", "accommodation", "apply", "room", "stay", "residence", "dormitory"]
        },
        {
            "question": "Is hostel available?",
            "answer": "Yes, GSSSIETW provides hostel facilities for women students.",
            "keywords": ["hostel", "accommodation", "girls"]
        },
        {
            "question": "How many hostel blocks are there?",
            "answer": "The hostel has three blocks with accommodation for around 400 students.",
            "keywords": ["hostel", "blocks", "400"]
        },
        {
            "question": "How many students stay in one room?",
            "answer": "Each hostel room is designed for three students.",
            "keywords": ["room", "hostel", "three"]
        },
        {
            "question": "Is the hostel safe?",
            "answer": "Yes, the hostel has CCTV surveillance and wardens for student safety.",
            "keywords": ["CCTV", "warden", "safety"]
        },
        {
            "question": "What facilities are available in the hostel?",
            "answer": "Each room includes a cot, study table, wardrobe, chair, and attached bathroom.",
            "keywords": ["cot", "study table", "wardrobe", "bathroom"]
        },
        {
            "question": "Is vegetarian food available?",
            "answer": "Yes, hygienic vegetarian food is served in the hostel.",
            "keywords": ["food", "vegetarian", "hostel"]
        },
        {
            "question": "What is the hostel curfew timing?",
            "answer": "The hostel gates close at 6:00 PM on weekdays and 6:00 PM on weekends. Students needing "
                      "late entry must inform the warden in advance with a valid reason.",
            "keywords": ["curfew", "hostel", "timing", "gate", "close", "entry", "warden"]
        },
    ],
    "Academics & Courses": [
        {
            "question": "What courses are offered?",
            "answer": "The college offers B.E., M.Tech, MBA, and Ph.D. programs.",
            "keywords": ["courses", "B.E.", "M.Tech", "MBA", "Ph.D."]
        },
        {
            "question": "How many B.E. branches are available?",
            "answer": "GSSSIETW offers six B.E. engineering branches.",
            "keywords": ["B.E.", "branches", "engineering"]
        },
        {
            "question": "Does the college offer M.Tech?",
            "answer": "Yes, the college offers two M.Tech programs.",
            "keywords": ["M.Tech", "postgraduate", "course"]
        },
        {
            "question": "Is MBA available?",
            "answer": "Yes, MBA is offered at GSSSIETW.",
            "keywords": ["MBA", "management"]
        },
        {
            "question": "Are Ph.D. programs available?",
            "answer": "Yes, Ph.D. programs are available in multiple departments.",
            "keywords": ["Ph.D.", "research"]
        },
        {
            "question": "Is ECE NBA accredited?",
            "answer": "Yes, the Electronics and Communication Engineering department is NBA accredited.",
            "keywords": ["ECE", "NBA", "department"]
        },
        {
            "question": "How can I get a transcript or bonafide certificate?",
            "answer": "Apply online via the Student Portal under 'Certificate Requests'. Transcripts take 5-7 "
                      "working days and bonafide certificates take 2-3 working days. Collect from the Academic "
                      "Office or opt for digital delivery.",
            "keywords": ["transcript", "bonafide", "certificate", "document", "request", "academics"]
        },
        {
            "question": "What is the process for branch/course transfer?",
            "answer": "Branch transfer requests are considered at the end of the first year, based on CGPA and "
                      "seat availability. Submit an application to the Dean of Academics during the transfer "
                      "window (usually in June).",
            "keywords": ["branch", "transfer", "course change", "switch branch", "department change"]
        },
    ],
    "Placements & Internships": [
        {
            "question": "Does the college provide placements?",
            "answer": "Yes, GSSSIETW has a dedicated Training and Placement Department.",
            "keywords": ["placement", "job", "career"]
        },
        {
            "question": "Is placement training provided?",
            "answer": "Yes, students receive aptitude, technical, and interview training.",
            "keywords": ["training", "aptitude", "interview"]
        },
        {
            "question": "Are mock interviews conducted?",
            "answer": "Yes, mock interviews are part of placement preparation.",
            "keywords": ["mock interview", "placement"]
        },
        {
            "question": "Are internships supported?",
            "answer": "Yes, the Placement Department supports internships and industry exposure.",
            "keywords": ["internship", "industry", "training"]
        },
        {
            "question": "Do companies visit for campus recruitment?",
            "answer": "Yes, companies visit the campus for recruitment drives.",
            "keywords": ["campus", "recruitment", "companies"]
        },
        {
            "question": "Does the college have industry collaborations?",
            "answer": "Yes, the college has industry collaborations and MoUs.",
            "keywords": ["MoU", "industry", "collaboration"]
        },
    ],
    "IT & Campus Services": [
        {
            "question": "How do I reset my student portal password?",
            "answer": "Click 'Forgot Password' on the login page and verify via your registered email/phone OTP. "
                      "If that fails, visit the IT Help Desk (Room 5, IT Block) with your student ID for a manual reset.",
            "keywords": ["password", "reset", "portal", "login", "forgot", "account", "it help"]
        },
        {
            "question": "Does the campus have Wi-Fi?",
            "answer": "Yes, the campus provides IT infrastructure to support students.",
            "keywords": ["Wi-Fi", "internet", "campus"]
        },
        {
            "question": "Is CCTV available?",
            "answer": "Yes, CCTV cameras are installed across the campus.",
            "keywords": ["CCTV", "security"]
        },
        {
            "question": "Is power backup available?",
            "answer": "Yes, the campus has power backup facilities.",
            "keywords": ["power backup", "electricity"]
        },
        {
            "question": "Are elevators available?",
            "answer": "Yes, elevators are available in all buildings.",
            "keywords": ["elevator", "lift"]
        },
        {
            "question": "Is purified drinking water available?",
            "answer": "Yes, purified drinking water is available on campus.",
            "keywords": ["drinking water", "water"]
        },
        {
            "question": "Is there a canteen?",
            "answer": "Yes, the campus has a spacious canteen and coffee shop.",
            "keywords": ["canteen", "coffee", "food"]
        },
        {
            "question": "Where can I report a technical issue on campus?",
            "answer": "Technical issues (WiFi, portal, projector, lab computers) can be reported at the IT Help "
                      "Desk (D block) or by raising a ticket through this Help Desk under 'IT & Technical'.",
            "keywords": ["technical", "issue", "report", "problem", "broken", "not working", "it"]
        },
    ],
    "College Timings": [
        {
        "question": "What are the college timings?",
        "answer": "The college starts at 9:00PM and ens at 4:15PM.",
        "keywords": ["college timings", "timing", "working hours"]
        },
        {
        "question": "What time does the college start?",
        "answer": "The college start time 9:00AM.",
        "keywords": ["start time", "college starts", "morning"]
        },
        {
        "question": "What time does the college end?",
        "answer": "The college closing time is 4:15PM.",
        "keywords": ["end time", "closing time", "college ends"]
        },
        {
        "question": "When does the college open?",
        "answer": "The college opens at 9:00AM.",
        "keywords": ["open", "opening time", "college open"]
        },
        {
        "question": "When does the college close?",
        "answer": "The college closes at 4:15PM.",
        "keywords": ["close", "closing time", "college close"]
        },
        {
        "question": "Is the college close on Saturday?",
        "answer": "College is holiday on 1st and 3rd Saturday.",
        "keywords": ["Saturday", "weekend", "working day"]
        },
        {
        "question": "Is the college open on Sunday?",
        "answer": "Sunday is generally a holiday",
        "keywords": ["Sunday", "holiday", "weekend"]
        },
    ],
    "Transport": [
        {
            "question": "Does GSSSIETW provide transport?",
            "answer": "Yes, the college provides transport facilities for students.",
            "keywords": ["transport", "bus"]
        },
        {
            "question": "How many buses does the college have?",
            "answer": "The college operates 17 buses covering different parts of Mysuru.",
            "keywords": ["17 buses", "transport", "Mysuru"]
        },
        {
            "question": "Do buses cover Mysuru?",
            "answer": "Yes, buses operate from different parts of Mysuru.",
            "keywords": ["bus routes", "Mysuru"]
        },
        {
            "question": "Is transport available for day scholars?",
            "answer": "Yes, transport is available for commuting students.",
            "keywords": ["day scholar", "bus"]
        },
        {
            "question": "Where can I find bus route information?",
            "answer": "Bus route details are available through the college transport section.",
            "keywords": ["bus route", "transport"]
        },
        {
            "question": "Is transport available from different areas?",
            "answer": "Yes, college buses cover various areas of Mysuru.",
            "keywords": ["areas", "transport", "bus"]
        },
    ],
    "Lost & Found": [
        {
            "question": "I lost something on campus, what should I do?",
            "answer": "Head to the **Lost & Found** section in this Help Desk and post a 'Lost' report with a "
                      "description, last seen location, and your contact details. It'll appear on the notice "
                      "board, and you'll also be notified if someone reports finding a matching item.",
            "keywords": ["lost", "missing", "find", "misplaced", "found", "item"]
        },
        {
            "question": "I found an item on campus, how do I report it?",
            "answer": "Thank you for being honest! Go to the **Lost & Found** section and post a 'Found' report "
                      "with a description, where you found it, and your contact details. It will be listed on "
                      "the notice board so the owner can claim it. You can also drop physical items at the "
                      "Admin Block reception.",
            "keywords": ["found", "item", "report", "submit", "return", "lost"]
        },
    ],
    "Canteen": [
        {
            "question": "Where can I see the canteen food menu?",
            "answer": "Check the **Canteen** section in this Help Desk for the full weekly menu (Breakfast, "
                      "Lunch, Snacks, and Dinner for every day) along with mess timings.",
            "keywords": ["canteen", "menu", "food", "mess", "timetable", "timing"]
        },
        {
            "question": "How do I give feedback about canteen food?",
            "answer": "Visit the **Canteen** section and use the Daily Food Feedback form to rate the meal and "
                      "leave comments. Your feedback helps the mess committee improve food quality.",
            "keywords": ["feedback", "canteen", "food", "rate", "review", "complaint", "mess"]
        },
    ],
    "Rules & Regulations": [
        {
            "question": "Where can I read the college rules and regulations?",
            "answer": "All official rules — academic conduct, attendance, examinations, hostel, anti-ragging, "
                      "dress code, and disciplinary policy — are listed in the **Rules & Regulations** section "
                      "of this Help Desk.",
            "keywords": ["rules", "regulations", "policy", "policies", "code of conduct", "discipline"]
        },
    ],
    "Certificates & IDs": [
        {
            "question": "How do I apply for a bonafide certificate, transport certificate, bus pass, or ID card?",
            "answer": "Go to the **Apply Online** section in this Help Desk. Choose the certificate type "
                      "(Bonafide Certificate, Transport Certificate, Bus Pass, or ID Card), fill in the form, "
                      "and submit. You can track your application status from the same section.",
            "keywords": ["bonafide", "transport certificate", "bus pass", "id card", "apply", "certificate", "application"]
        },
    ],
}


def get_categories():
    """Return list of all knowledge base categories."""
    return list(KNOWLEDGE_BASE.keys())


def get_all_faqs_flat():
    """Return a flat list of (category, faq_item) tuples."""
    flat = []
    for category, faqs in KNOWLEDGE_BASE.items():
        for item in faqs:
            flat.append((category, item))
    return flat
