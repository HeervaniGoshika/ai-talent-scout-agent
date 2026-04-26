from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def keyword_overlap(jd_skills, candidate_skills):
    if not jd_skills:
        return 0, []

    matched = list(set(jd_skills) & set(candidate_skills))
    score = len(matched) / len(jd_skills)

    return score, matched


def match_candidates(parsed_jd, candidates):

    jd_text = " ".join(parsed_jd["skills"])
    jd_embedding = model.encode(jd_text)

    results = []

    for c in candidates:
        profile_text = " ".join(c["skills"])
        emb = model.encode(profile_text)

        sim = cosine_similarity([jd_embedding], [emb])[0][0]

        overlap_score, matched_skills = keyword_overlap(
            parsed_jd["skills"], c["skills"]
        )

        match_score = max(0, (0.7 * sim + 0.3 * overlap_score)) * 100

        c["match_score"] = float(match_score)
        c["matched_skills"] = matched_skills
        c["missing_skills"] = list(set(parsed_jd["skills"]) - set(c["skills"]))

        results.append(c)

    return results