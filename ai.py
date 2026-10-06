import streamlit as st
from textblob import TextBlob
import pandas as pd
from datetime import datetime

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Product Feedback Assistant",
    page_icon="💬",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = []

if "rating" not in st.session_state:
    st.session_state.rating = 3


# ---------------- FUNCTIONS ----------------

def analyze_sentiment(feedback):
    polarity = TextBlob(feedback).sentiment.polarity

    if polarity > 0.1:
        return "Positive 😊"
    elif polarity < -0.1:
        return "Negative 😞"
    else:
        return "Neutral 😐"


def detect_issues(feedback):
    text = feedback.lower()
    issues = []

    issue_keywords = {
        "Delivery": [
            "delivery", "late", "delay",
            "delayed", "shipping"
        ],
        "Product Quality": [
            "quality", "broken", "damaged",
            "defect", "defective"
        ],
        "Price": [
            "price", "expensive", "cost",
            "costly"
        ],
        "Customer Support": [
            "support", "customer service",
            "response", "respond"
        ],
        "Payment": [
            "payment", "refund", "upi",
            "transaction"
        ],
        "Technical Issue": [
            "error", "bug", "crash",
            "login", "not working", "technical"
        ]
    }

    for issue, keywords in issue_keywords.items():
        for keyword in keywords:
            if keyword in text:
                issues.append(issue)
                break

    if not issues:
        issues.append("No specific issue detected")

    return issues


def get_suggestion(sentiment, issues):
    if "Delivery" in issues:
        return "Improve delivery speed and tracking."

    if "Product Quality" in issues:
        return "Improve product quality and packaging."

    if "Price" in issues:
        return "Consider providing better pricing or discounts."

    if "Customer Support" in issues:
        return "Improve customer support response time."

    if "Payment" in issues:
        return "Improve payment and refund processing."

    if "Technical Issue" in issues:
        return "Fix technical problems and improve system reliability."

    if sentiment == "Positive 😊":
        return "Thank you! We are happy that you liked the product."

    if sentiment == "Negative 😞":
        return "We are sorry about your experience. We will work to improve it."

    return "Thank you for your feedback. We will use it to improve our product."


def get_priority(sentiment, issues, rating):
    if sentiment == "Negative 😞":
        if rating <= 2 or len(issues) >= 2:
            return "High 🔴"
        return "Medium 🟠"

    if rating == 3:
        return "Medium 🟠"

    return "Low 🟢"


# ---------------- TITLE ----------------

st.title("💬 Product Feedback Assistant")
st.write("Enter your product feedback and get an instant analysis.")

st.divider()


# ---------------- FEEDBACK INPUT ----------------

st.subheader("📝 Enter Your Feedback")

feedback = st.text_area(
    "Your Feedback",
    placeholder="Example: The product quality is good, but delivery was late.",
    height=120
)


# ---------------- STAR RATING ----------------

st.subheader("⭐ Rate the Product")

cols = st.columns(5)

for i in range(1, 6):
    if cols[i - 1].button(
        "⭐",
        key=f"star_{i}",
        use_container_width=True
    ):
        st.session_state.rating = i

rating = st.session_state.rating

st.write("Selected Rating:", "⭐" * rating)


# ---------------- ANALYZE BUTTON ----------------

if st.button("🔍 Analyze Feedback", use_container_width=True):

    feedback_clean = feedback.strip()

    # Validation
    if not feedback_clean:
        st.warning("⚠️ Please enter your feedback.")

    elif feedback_clean.isdigit():
        st.warning("⚠️ Please enter a proper feedback sentence, not only a number.")

    elif len(feedback_clean) < 5:
        st.warning("⚠️ Please enter a little more feedback.")

    else:
        # Analysis
        sentiment = analyze_sentiment(feedback_clean)
        issues = detect_issues(feedback_clean)
        suggestion = get_suggestion(sentiment, issues)
        priority = get_priority(sentiment, issues, rating)

        # ---------------- RESULT ----------------

        st.divider()

        st.subheader("📊 Feedback Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Sentiment", sentiment)

        with col2:
            st.metric("Priority", priority)

        with col3:
            st.metric("Rating", f"{rating}/5")

        st.write("### 🔎 Detected Issues")

        for issue in issues:
            st.write(f"• {issue}")

        st.write("### 💡 Suggestion")
        st.info(suggestion)

        # ---------------- SAVE FEEDBACK ----------------

        record = {
            "Date & Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Feedback": feedback_clean,
            "Rating": rating,
            "Sentiment": sentiment,
            "Issue": ", ".join(issues),
            "Priority": priority,
            "Suggestion": suggestion
        }

        st.session_state.feedback_history.append(record)

        st.success("✅ Feedback analyzed and saved successfully!")


# ---------------- DASHBOARD ----------------

st.divider()

st.subheader("📈 Feedback Dashboard")

total_feedback = len(st.session_state.feedback_history)

positive_count = sum(
    1 for item in st.session_state.feedback_history
    if item["Sentiment"] == "Positive 😊"
)

negative_count = sum(
    1 for item in st.session_state.feedback_history
    if item["Sentiment"] == "Negative 😞"
)

if total_feedback > 0:
    average_rating = sum(
        item["Rating"]
        for item in st.session_state.feedback_history
    ) / total_feedback
else:
    average_rating = 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Feedback", total_feedback)

with col2:
    st.metric("Positive", positive_count)

with col3:
    st.metric("Negative", negative_count)

with col4:
    st.metric("Average Rating", f"{average_rating:.1f}/5")


# ---------------- FEEDBACK HISTORY ----------------

st.divider()

st.subheader("📋 Feedback History")

if st.session_state.feedback_history:

    df = pd.DataFrame(st.session_state.feedback_history)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # CSV download
    csv = df.to_csv(index=False)

    st.download_button(
        label="⬇️ Download Feedback CSV",
        data=csv,
        file_name="product_feedback.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info("No feedback submitted yet.")


# ---------------- CLEAR HISTORY ----------------

st.divider()

if st.button("🗑️ Clear Feedback History", use_container_width=True):

    st.session_state.feedback_history = []

    st.success("✅ Feedback history cleared.")

    st.rerun()


# ---------------- FOOTER ----------------

st.divider()

st.caption("💬 Product Feedback Assistant | AI-Based Feedback Analysis")