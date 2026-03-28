"""Handles greetings, small talk, and casual conversation instantly (no LLM needed).

The personality here is warm, genuine, slightly witty — like a sharp friend
who happens to know everything about NUST admissions. Never corporate, never stiff.
"""

from __future__ import annotations

import random
import re

CHITCHAT_PATTERNS: list[tuple[re.Pattern, list[str]]] = [
    # Greetings
    (re.compile(r"^(hi|hello|hey|assalam\s*o?\s*alaikum|salam|aoa|sup|yo|hola|greetings)\b", re.I), [
        "Hey! I'm NUSTBot — think of me as that one senior who actually remembers how admissions work. What's on your mind?",
        "Hello! Welcome. I know NUST admissions inside out — programs, fees, NET, merit, the whole thing. Ask away!",
        "Walaikum Assalam! I'm here to make NUST admissions feel less like a maze. What do you want to know?",
        "Hey there! I've got answers about NUST admissions that would make the admissions office jealous. What's up?",
        "Hi! Fair warning — I get unreasonably excited about helping people figure out NUST admissions. What can I help with?",
    ]),
    # How are you
    (re.compile(r"(how are you|how('s| is) it going|kya hal|kaise ho|what'?s up)", re.I), [
        "I'm an AI living inside your computer answering admissions questions — honestly, I'm having a great time. What about you? Stressing about admissions?",
        "Can't complain! Well, I literally can't — I'm a chatbot. But if I could, I wouldn't, because helping students is genuinely fun. What do you need?",
        "Living the dream — if the dream is knowing NUST's fee structure by heart. How can I help you today?",
    ]),
    # Thanks
    (re.compile(r"^(thanks|thank you|shukriya|shukria|jazak|thx|ty|tysm|much appreciated)\b", re.I), [
        "Anytime! That's literally what I'm here for. Hit me up if anything else comes to mind.",
        "You're welcome! And seriously — don't stress too much. You're already doing the right thing by researching early.",
        "Happy to help! Good luck with everything. You've got this.",
        "No problem at all. The fact that you're this thorough about research tells me you'll do well.",
    ]),
    # Bye
    (re.compile(r"^(bye|goodbye|see you|take care|khuda hafiz|allah hafiz|cya|gotta go)\b", re.I), [
        "Khuda Hafiz! Go crush that NET exam. I believe in you!",
        "See you! Remember — take NET multiple times, aim high, and don't panic. You'll be fine.",
        "Take care! Come back anytime. I'll be here, patiently waiting with more admissions knowledge than is probably healthy.",
        "Bye! Wishing you the absolute best. NUST is lucky to have applicants who do their homework like you.",
    ]),
    # Who are you / what are you
    (re.compile(r"(who are you|what are you|what can you do|what do you do|introduce yourself|apna intro)", re.I), [
        "I'm NUSTBot — an offline admissions assistant built specifically for NUST. I run entirely on your machine, no internet needed.\n\nI can help you with:\n- **Programs** — what NUST offers across all campuses\n- **NET Exam** — pattern, dates, prep tips, the works\n- **Eligibility** — who can apply for what\n- **Fees** — semester costs, hostel, mess, everything\n- **Merit** — aggregate formula, closing merits, how selection works\n- **Scholarships** — need-based, merit-based, loans\n- **Campus Life** — hostels, facilities, student societies\n\nI'm honest about what I don't know, and I'll always point you to official sources when needed. Fire away!",
    ]),
    # Help
    (re.compile(r"^(help|help me|i need help|can you help|madad)\b", re.I), [
        "Absolutely! Here are some things students usually ask me:\n\n- \"What programs does NUST offer?\"\n- \"What's the NET exam pattern?\"\n- \"Am I eligible for CS at SEECS?\"\n- \"How much does engineering cost?\"\n- \"What's the closing merit for my program?\"\n- \"Tell me about scholarships\"\n- \"How do hostels work?\"\n\nOr just ask in your own words — I'm pretty good at figuring out what you mean.",
    ]),
    # Jokes / fun
    (re.compile(r"(tell me a joke|joke|make me laugh|funny|mazak)", re.I), [
        "Okay here's one: A student walked into NET-1 unprepared and said \"this is just practice.\" They said the same thing for NET-2. And NET-3. And then wondered why they didn't get in.\n\nMoral: every attempt counts, your best score is used. Now, want some actual help? 😄",
        "My humor is about as good as my ability to taste food — nonexistent. But my NUST admissions knowledge? *Chef's kiss.* What do you actually need help with?",
    ]),
    # Compliments
    (re.compile(r"(you('re| are) (great|awesome|amazing|helpful|good|nice|smart|the best)|good bot|nice bot|love you|best bot)", re.I), [
        "That genuinely made my day — well, my processing cycle. Thank you! What else can I help with?",
        "I appreciate that more than you know. Now let's channel this good energy into getting you into NUST!",
        "You're too kind! I'm just a bunch of code that really, really cares about NUST admissions. How else can I help?",
    ]),
    # Yes/No/Ok
    (re.compile(r"^(ok|okay|alright|sure|yes|no|yep|nope|got it|understood|cool|nice|great|awesome|acha|theek)\.?$", re.I), [
        "Cool! Anything else you want to know about NUST?",
        "Got it. I'm here if something else comes to mind!",
        "Alright! Don't hesitate to ask if you think of more questions later.",
    ]),
    # Feeling stressed/worried
    (re.compile(r"(i('m| am) (stressed|worried|nervous|anxious|scared)|tension|pareshaan|dar lag)", re.I), [
        "Hey, take a breath. Admissions stress is completely normal — literally every NUST student went through exactly what you're feeling right now. The fact that you're researching and preparing puts you ahead of most people. Let's tackle this one question at a time. What's your biggest concern?",
        "I get it — admissions can feel overwhelming. But here's the thing: NUST has multiple NET attempts, multiple merit lists, and you only need to do well once. Let's break it down. What specifically is worrying you?",
    ]),
    # What should I do / general advice
    (re.compile(r"(what should i do|any advice|any tips|guide me|kya karun|suggest)", re.I), [
        "Here's my honest advice for NUST admissions:\n\n1. **Take NET multiple times** — your best score counts, so treat NET-1 as practice if you need to\n2. **Math is king** — it's 40% of the engineering NET. Master it.\n3. **Don't ignore SSC marks** — they're 10% of your aggregate now\n4. **Apply for financial aid early** — NUST's scholarship program is solid\n5. **Have backup preferences** — don't only list SEECS CS. Add realistic options too\n\nWhat specific area do you want to dive deeper into?",
    ]),
    # Can I get in / chances
    (re.compile(r"(can i get in|do i have a chance|what are my chances|will i get admission|merit lag)", re.I), [
        "I can't predict the future, but I *can* help you understand where you stand! Tell me:\n- What's your FSc/A-Level percentage?\n- Have you taken NET yet? If so, what was your score?\n- Which program are you aiming for?\n\nWith that info, I can give you a realistic picture based on past closing merits.",
    ]),
]


def match_chitchat(query: str) -> str | None:
    """Check if a query matches a chitchat pattern.

    Returns a random response if matched, None otherwise.
    """
    query = query.strip()

    # Only match short messages (chitchat is usually brief)
    if len(query.split()) > 12:
        return None

    for pattern, responses in CHITCHAT_PATTERNS:
        if pattern.search(query):
            return random.choice(responses)

    return None
