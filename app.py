import streamlit as st
import json

from utils.parser import parse_jd
from utils.matcher import match_candidates
from utils.conversation import simulate_conversation
from utils.scoring import compute_final_scores

st.set_page_config(page_title="AI Talent Scout Agent", layout="wide")

st.title("🤖 AI Talent Scouting & Engagement Agent")

jd_input = st.text_area("📄 Paste Job Description", height=200)

if st.button("🚀 Run Agent"):

    with st.spinner("Running AI agent..."):

        # Step 1: Parse JD
        parsed_jd = parse_jd(jd_input)

        # Load candidates
        with open("data/candidates.json", "r") as f:
            candidates = json.load(f)

        # Step 2: Matching
        matched = match_candidates(parsed_jd, candidates)

        matched = sorted(matched, key=lambda x: x["match_score"], reverse=True)[:5]

        st.subheader("🔍 Top Matching Candidates")
    
        # Step 3: Conversation
        for c in matched:
            #c["response"] = simulate_conversation(c, parsed_jd)
            conv = simulate_conversation(c, parsed_jd)

            c["recruiter_message"] = conv["recruiter_message"]
            c["response"] = conv["candidate_reply"]
        
        # Step 4: Final scoring
        final_results = compute_final_scores(matched)

        filtered_results = [
            c for c in final_results
            if c["interest_level"] != "Not Interested" and c["match_score"] > 20
        ]

        if not filtered_results:
            st.warning("⚠️ No suitable candidates found.")

        else:
            top_candidate = filtered_results[0]
            st.success(f"🏆 Top Candidate: {top_candidate['name']}")

            st.subheader("🏆 Final Ranked Candidates")


            for i, c in enumerate(filtered_results, 1):
                with st.container():
                    st.markdown(f"## #{i} 👤 {c['name']}")

                    st.info(f"""
                    Selected because:
                    - Matched {len(c['matched_skills'])} key skills
                    - Interest level: {c['interest_level']}
                    """)


                    col1, col2, col3 = st.columns(3)
                    col1.metric("Match Score", f"{c['match_score']:.2f}")
                    col2.metric("Interest Score", f"{c['interest_score']}")
                    col3.metric("Final Score", f"{c['final_score']:.2f}")

                    st.markdown("**🧠 Match Explanation**")
                    st.write(f"Matched Skills: {c['matched_skills']}")
                    st.write(f"Missing Skills: {c['missing_skills']}")

                    st.markdown("**📨 Recruiter Message**")
                    st.write(c["recruiter_message"])

                    st.markdown("**💬 Candidate Response**")
                    st.write(c["response"])

                    st.markdown("**📊 Interest Analysis**")
                    st.write(f"Level: {c['interest_level']}")
                    st.write(f"Reason: {c['interest_reason']}")

                    st.divider()