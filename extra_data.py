"""
Static reference data for the College Help Desk: canteen menu, rules &
regulations, and the certificate/ID application catalog.
"""

CANTEEN_MENU = {
    "Monday": {
        "Breakfast": "Idli, Sambar, Coconut Chutney, Tea/Coffee",
        "Lunch": "Rice, Dal Tadka, Mixed Veg Curry, Curd, Papad",
        "Snacks": "Samosa, Masala Chai",
        "Dinner": "Chapati, Paneer Butter Masala, Jeera Rice, Salad",
    },
    "Tuesday": {
        "Breakfast": "Poha, Boiled Sprouts, Tea/Coffee",
        "Lunch": "Rice, Rajma, Aloo Gobi, Curd, Pickle",
        "Snacks": "Vada Pav, Buttermilk",
        "Dinner": "Chapati, Chicken/Soya Curry, Vegetable Pulao, Salad",
    },
    "Wednesday": {
        "Breakfast": "Uttapam, Tomato Chutney, Tea/Coffee",
        "Lunch": "Rice, Sambar, Cabbage Poriyal, Curd, Papad",
        "Snacks": "Bread Pakora, Masala Chai",
        "Dinner": "Chapati, Egg/Mushroom Curry, Jeera Rice, Salad",
    },
    "Thursday": {
        "Breakfast": "Aloo Paratha, Curd, Pickle, Tea/Coffee",
        "Lunch": "Rice, Dal Fry, Bhindi Masala, Curd, Papad",
        "Snacks": "Sandwich, Cold Coffee",
        "Dinner": "Chapati, Chole, Vegetable Fried Rice, Salad",
    },
    "Friday": {
        "Breakfast": "Dosa, Sambar, Chutney, Tea/Coffee",
        "Lunch": "Rice, Sambar, Beans Curry, Curd, Papad",
        "Snacks": "Pav Bhaji, Masala Chai",
        "Dinner": "Chapati, Kadai Paneer, Veg Biryani, Raita",
    },
    "Saturday": {
        "Breakfast": "Upma, Coconut Chutney, Tea/Coffee",
        "Lunch": "Rice, Dal, Mixed Veg, Curd, Papad, Sweet",
        "Snacks": "Dhokla, Buttermilk",
        "Dinner": "Chapati, Veg Kofta, Pulao, Salad",
    },
    "Sunday": {
        "Breakfast": "Chole Bhature, Tea/Coffee",
        "Lunch": "Special Sunday Thali (Rice, Dal Makhani, Paneer, Sweet, Curd, Papad)",
        "Snacks": "Fruit Chaat, Cold Drink",
        "Dinner": "Chapati, Mix Veg, Fried Rice, Ice Cream",
    },
}

CANTEEN_TIMINGS = {
    "Breakfast": "7:30 AM – 9:30 AM",
    "Lunch": "12:00 PM – 2:30 PM",
    "Snacks": "4:30 PM – 6:00 PM",
    "Dinner": "7:30 PM – 9:30 PM",
}

RULES_REGULATIONS = {
    "Academic Conduct": [
        "Students must maintain academic honesty; plagiarism or cheating in any form leads to disciplinary action.",
        "Carrying mobile phones into examination halls is strictly prohibited.",
        "Students must carry their ID card at all times on campus.",
        "Use of unfair means in assignments, tests, or exams may result in suspension.",
    ],
    "Attendance Policy": [
        "A minimum of 75% attendance is mandatory in each subject to be eligible for exams.",
        "Attendance shortage may be condoned only with valid medical or extenuating documentation, subject to Dean's approval.",
        "Students with attendance below 65% will not be permitted to appear for end-semester exams under any circumstances.",
    ],
    "Examination Rules": [
        "Students must be seated 15 minutes before the exam start time.",
        "Possession of unauthorized material during exams is treated as malpractice.",
        "Re-evaluation requests must be submitted within 10 days of result declaration.",
        "Late entry may not be permitted.",
    ],
    "Hostel Rules": [
        "Hostel gates close at 6:00 PM on weekdays and 6:00 PM on weekends.",
        "Visitors are allowed only in designated common areas during visiting hours.",
        "Consumption of alcohol, smoking, or possession of prohibited substances in hostel premises is strictly banned.",
        "Damage to hostel property will be charged to the responsible student(s).",
        "During weekdays, students must obtain permission from the concerned authority before going outside.",
    ],
    "Anti-Ragging Policy": [
        "Ragging in any form is a criminal offense and strictly prohibited on and off campus.",
        "Any student found guilty of ragging will face immediate suspension/expulsion and legal action as per UGC regulations.",
        "Students facing ragging should report immediately to the Anti-Ragging Committee or Student Counselling Cell.",
    ],
    "Dress Code": [
        "Students are expected to dress in a decent, presentable manner appropriate for an academic environment.",
        "Jeans, short dresses, and sleeveless outfits are not permitted.",
        "Students must wear the prescribed college uniform on designated days.",
        "On Wednesdays, students may wear decent-coloured traditional attire such as a kurta.",
    ],
    "Disciplinary Actions": [
        "Misconduct, harassment, or violence against staff/students will lead to strict disciplinary action, including expulsion.",
        "Damage to college property will result in fines and possible suspension.",
        "Repeated violations of college rules will be reviewed by the Disciplinary Committee.",
    ],
}

# Each application type: description, processing time, and any extra fields
# (beyond the common name/roll no/email/phone) collected on the form.
APPLICATION_TYPES = {
    "Bonafide Certificate": {
        "description": "An official certificate confirming you are a currently enrolled student. "
                        "Commonly needed for bank loans, passport applications, or visa processing.",
        "processing_time": "2-3 working days",
        "extra_fields": ["Purpose (e.g., bank loan, passport, visa, scholarship)"],
    },
    "Transport Certificate": {
        "description": "Certifies your use of college transport, often required for local authority "
                        "verification or concession passes.",
        "processing_time": "3-4 working days",
        "extra_fields": ["Bus Route Number", "Pickup Point"],
    },
    "Bus Pass": {
        "description": "Apply for a new or renewed college bus pass for a specific route and duration.",
        "processing_time": "5-7 working days",
        "extra_fields": ["Preferred Route", "Pickup Point", "Duration (Semester / Annual)"],
    },
    "ID Card (New / Duplicate / Renewal)": {
        "description": "Apply for a new student ID card, a duplicate (if lost/damaged), or a renewal "
                        "for the new academic year.",
        "processing_time": "4-5 working days",
        "extra_fields": ["Reason (New / Lost / Damaged / Renewal)"],
    },
}
