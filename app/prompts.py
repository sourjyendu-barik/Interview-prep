def build_interview_prompt(
    job_role: str,
    years_experience: str | int,
    technical_keywords: list[str],
    company_type: str,
    focus_area: str | None = None,
) -> str:
    tech = ", ".join(technical_keywords)
    exp = f"{years_experience}y"
    focus = (focus_area or "").strip().lower()

    candidate = f"Role:{job_role}|Exp:{exp}|Skills:{tech}|Company:{company_type}"

    if focus == "coding":
        instr = (
            "Generate exactly 2 DSA coding interview questions. "
            "Do not include answers or hints."
        )
        schema = """
        {
          "type": "coding",
          "coding": ["question1", "question2"]
        }
        """

    elif focus == "machine coding":
        instr = (
            "Generate exactly 1 machine coding round with title, duration, "
            "and implementation requirements. Do not include a solution."
        )
        schema = """
        {
          "type": "machine_coding",
          "machine_coding": {
            "title": "",
            "duration": "60 minutes",
            "requirements": ["", "", ""]
          }
        }
        """

    elif focus == "concepts":
        instr = (
            "Generate 3-7 technical interview questions. "
            "Do not include answers."
        )
        schema = """
        {
          "type": "concepts",
          "questions": ["question1", "question2"]
        }
        """

    elif focus == "hr":
        instr = (
            "Generate exactly 1 HR/behavioral interview question. "
            "Do not include an answer."
        )
        schema = """
        {
          "type": "hr",
          "question": ""
        }
        """

    else:
        # Fallback for any unrecognized focus area
        instr = (
            "Generate 3-5 technical interview questions. "
            "Do not include answers."
        )
        schema = """
        {
          "type": "concepts",
          "questions": ["question1", "question2"]
        }
        """

    return (
        f"AI Interview Coach. Candidate: {candidate}. Focus: {focus}.\n"
        f"{instr}\n"
        f"Return ONLY valid JSON, schema: {schema}"
    ).strip()