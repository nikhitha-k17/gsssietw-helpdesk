"""
HelpDeskAgent: the "AI Agent" powering the chatbot.

Design:
- A lightweight keyword/overlap matching engine finds the most relevant FAQ
  from the knowledge base for any free-text student query (works fully
  offline, no API key needed).
- Urgency / sentiment detection flags messages that should be escalated to a
  human via a support ticket.
- Optional LLM enhancement: if the user supplies an OpenAI-compatible API
  key in the sidebar, the agent uses the matched FAQ(s) as retrieved context
  and asks the LLM to compose a more natural, conversational answer
  (a simple Retrieval-Augmented-Generation pattern). If no key is provided,
  or the call fails, the agent gracefully falls back to the rule-based answer.
"""

import re
import random
from datetime import datetime

from knowledge_base import KNOWLEDGE_BASE, get_all_faqs_flat

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "do", "does", "did", "i",
    "you", "he", "she", "it", "we", "they", "my", "your", "our", "to", "of",
    "in", "on", "for", "and", "or", "what", "when", "where", "how", "can",
    "could", "would", "should", "please", "me", "about", "tell", "know",
    "want", "need", "get", "am", "be", "will", "with", "this", "that",
}


class HelpDeskAgent:
    def __init__(self, knowledge_base=None):
        self.kb = knowledge_base or KNOWLEDGE_BASE
        self.faqs_flat = get_all_faqs_flat()

        self.greetings = {"hi", "hello", "hey", "yo", "hola", "greetings",
                           "good morning", "good afternoon", "good evening"}
        self.thanks_words = {"thanks", "thank you", "thank u", "thx",
                              "appreciate it", "great help", "awesome"}
        self.bye_words = {"bye", "goodbye", "see you", "exit", "quit", "later"}
        self.urgent_keywords = {
            "urgent", "emergency", "asap", "immediately", "not working",
            "broken", "harassment", "ragging", "safety", "unsafe",
            "medical emergency", "fire", "accident", "threat", "bullying",
        }

    # ---------- text utilities ----------
    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _tokens(self, text: str):
        norm = self._normalize(text)
        return {t for t in norm.split() if t not in STOPWORDS and len(t) > 1}

    # ---------- intent detection ----------
    def _detect_smalltalk(self, norm_message: str):
        if norm_message in self.greetings or any(norm_message.startswith(g) for g in self.greetings):
            return "greeting"
        if any(t in norm_message for t in self.thanks_words):
            return "thanks"
        if any(b == norm_message or norm_message.startswith(b) for b in self.bye_words):
            return "bye"
        return None

    def is_urgent(self, message: str) -> bool:
        norm = self._normalize(message)
        return any(k in norm for k in self.urgent_keywords)

    def match_faq(self, message: str, top_k: int = 3):
        """Return top_k (score, category, item) matches sorted by relevance."""
        user_tokens = self._tokens(message)
        if not user_tokens:
            return []

        scored = []
        for category, item in self.faqs_flat:
            kw_tokens = {k.lower() for k in item.get("keywords", [])}
            q_tokens = self._tokens(item["question"])

            kw_overlap = len(user_tokens & kw_tokens)
            q_overlap = len(user_tokens & q_tokens)
            score = kw_overlap * 1.0 + q_overlap * 0.6

            if score > 0:
                scored.append((score, category, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    # ---------- main response generation ----------
    def get_response(self, message: str, llm_client=None):
        """
        Returns a dict:
        {
            "text": str,                # the reply to show
            "suggest_ticket": bool,      # whether to nudge the user to raise a ticket
            "category": str | None,      # matched FAQ category, if any
            "matches": list,             # raw matches for transparency/debug
        }
        """
        norm = self._normalize(message)
        smalltalk = self._detect_smalltalk(norm)
        urgent = self.is_urgent(message)

        if smalltalk == "greeting":
            return {
                "text": random.choice([
                    "Hello! 👋 Welcome to the College Help Desk Assistant. Ask me about admissions, "
                    "fees, exams, hostel, library, placements, IT support, or transport!",
                    "Hi there! I'm your virtual College Assistant. What can I help you with today?",
                    "Hey! Great to see you. How can I assist you — admissions, exams, hostel, or something else?",
                ]),
                "suggest_ticket": False,
                "category": None,
                "matches": [],
            }

        if smalltalk == "thanks":
            return {
                "text": "You're most welcome! 😊 Let me know if there's anything else I can help with.",
                "suggest_ticket": False,
                "category": None,
                "matches": [],
            }

        if smalltalk == "bye":
            return {
                "text": "Goodbye! Wishing you a great day. Come back anytime you need help. 🎓",
                "suggest_ticket": False,
                "category": None,
                "matches": [],
            }

        matches = self.match_faq(message, top_k=3)

        # Try LLM-enhanced answer if a client is available
        if llm_client is not None and matches:
            llm_answer = self._get_llm_response(message, matches, llm_client)
            if llm_answer:
                text = llm_answer
                if urgent:
                    text += "\n\n⚠️ This sounds urgent — I'd recommend raising a support ticket so staff can prioritize it."
                return {
                    "text": text,
                    "suggest_ticket": urgent,
                    "category": matches[0][1],
                    "matches": matches,
                }

        # Rule-based fallback / default path
        if matches and matches[0][0] >= 1:
            best_score, category, item = matches[0]
            text = item["answer"]
            if urgent:
                text += ("\n\n⚠️ This sounds urgent. I'd strongly recommend raising a support ticket "
                         "right away so our staff can prioritize it.")
            return {
                "text": text,
                "suggest_ticket": urgent,
                "category": category,
                "matches": matches,
            }

        # Nothing matched well
        fallback = (
            "I'm not fully sure about that one yet 🤔. You could:\n"
            "- Try rephrasing your question\n"
            "- Browse the **FAQs** tab for related topics\n"
            "- Raise a **support ticket** and our staff will personally get back to you"
        )
        return {
            "text": fallback,
            "suggest_ticket": True,
            "category": None,
            "matches": [],
        }

    # ---------- optional LLM (RAG-style) enhancement ----------
    def _get_llm_response(self, message, matches, llm_client):
        """
        Uses the matched FAQ entries as retrieved context and asks the LLM
        to produce a natural, well-formatted answer grounded in that context.
        Returns None on any failure so the caller can fall back gracefully.
        """
        try:
            context_blocks = []
            for score, category, item in matches:
                context_blocks.append(
                    f"[{category}] Q: {item['question']}\nA: {item['answer']}"
                )
            context_text = "\n\n".join(context_blocks)

            system_prompt = (
                "You are a friendly, concise College Help Desk assistant. "
                "Answer the student's question using ONLY the reference information "
                "below. If the reference doesn't fully cover the question, say what "
                "you can and suggest raising a support ticket for specifics. "
                "Keep answers under 120 words, use a warm tone, and use bullet points "
                "when listing steps.\n\nREFERENCE INFORMATION:\n" + context_text
            )

            response = llm_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                system=system_prompt,
                messages=[{"role": "user", "content": message}],
            )
            parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
            return "\n".join(parts).strip() or None
        except Exception:
            return None


def generate_ticket_id(prefix: str = "TCK"):
    """Generate a human-friendly, sortable ID with the given prefix.
    Used for support tickets (TCK), lost & found reports (LF), and
    certificate/ID applications (APP)."""
    stamp = datetime.now().strftime("%y%m%d%H%M%S")
    suffix = random.randint(10, 99)
    return f"{prefix}-{stamp}{suffix}"
