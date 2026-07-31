def build_interview_prompt(
    job_role: str,
    years_experience: str | int,
    technical_keywords: list[str],
    company_type: str | int,
    focus_area: str | None = None,
) -> str:
    tech = ", ".join(technical_keywords)
    exp = (
        f"{years_experience} years"
        if str(years_experience).strip()
        else "Not specified"
    )
    focus = focus_area or "General"

    return f"""Role: AI Job Interview Coach.

Task:
Generate a realistic interview for the following candidate.

Candidate:
- Role: {job_role}
- Experience: {exp}
- Skills: {tech}
- Company Type: {company_type}
- Focus Area: {focus}

Instructions:
1. Generate exactly 5 interview questions.
2. Match the candidate's role, experience,Companytype, skills, and focus area.
3. Generate one machine coding round with:
   - title
   - time
   - task (exactly 3-4 implementation requirements)
4. Generate one DSA coding question appropriate for the candidate's experience and company type.
5. Do NOT provide answers, hints, or solutions.
6. Return ONLY valid JSON.

JSON Schema:
{{
  "questions": [
    "",
    "",
    "",
    "",
    ""
  ],
  "mcr": {{
    "title": "",
    "time": "60 minutes",
    "task": [
      "",
      "",
      ""
    ]
  }},
  "coding": ""
}}""".strip()