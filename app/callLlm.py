import os
import json
import logging

from fastapi import HTTPException
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger("uvicorn")

api_key = os.getenv("GEMINI_API")
if not api_key:
    raise RuntimeError("GEMINI_API is missing in .env")

client = genai.Client(api_key=api_key)


async def fetchLlm(prompt: str):
    try:
        logger.info("Sending request to Gemini...")
        response = await client.aio.models.generate_content(  # type: ignore

        model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
        response_mime_type="application/json"
            ),
        )

        logger.info("Gemini API call completed.")

        text = response.text

        if not text:
            logger.error("Gemini returned empty text")
            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty response."
            )

        logger.info("Raw Gemini response: %s", text)

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            logger.exception("Invalid JSON from Gemini")
            raise HTTPException(
                status_code=500,
                detail="Gemini returned invalid JSON."
            )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Gemini request failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to communicate with Gemini."
        )