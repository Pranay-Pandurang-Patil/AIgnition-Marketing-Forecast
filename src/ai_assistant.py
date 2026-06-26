import os

import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

MODEL = genai.GenerativeModel(
    "gemini-2.5-flash"
)
def generate_ai_analysis(
    forecast,
    scenario,
    days,
    total_budget,
    total_revenue,
    blended_roas
):
    """
    Generate business insights using Gemini AI.
    """

    if API_KEY is None:
        return (
            "Gemini API Key not found. "
            "Please configure the GEMINI_API_KEY "
            "inside the .env file."
        )

    table = forecast.to_string(index=False)

    prompt = f"""
You are a Senior Ecommerce Marketing Consultant helping digital marketing agencies
forecast ecommerce performance.

You are analyzing a machine learning forecast generated from historical
Google Ads, Meta Ads, and Microsoft Ads campaign performance.

Business Scenario
-----------------
Scenario: {scenario}

Forecast Horizon: {days} Days

Forecast Budget:
${total_budget:,.2f}

Forecast Revenue:
${total_revenue:,.2f}

Blended ROAS:
{blended_roas:.2f}

Forecast Results
----------------
{table}

Generate a professional business report with these sections.

## 1. Executive Summary
Provide a concise overview of the forecast.

## 2. Forecast Interpretation
Explain why the forecast looks reasonable using the supplied data.

## 3. Budget Allocation Analysis
Identify which channels perform best and which need optimization.

## 4. Revenue Drivers
Explain which platforms contribute most to expected revenue.

## 5. Operational Risks
Highlight dependency on one platform, low ROAS, uncertainty, or inefficient budget allocation.

## 6. Growth Opportunities
Identify practical opportunities to improve revenue or ROAS.

## 7. Budget Optimization Recommendations
Suggest realistic budget reallocations between Google, Meta, and Microsoft.

## 8. Key Takeaways
Provide 4–6 concise bullet points suitable for business stakeholders.

Rules:
- Do not invent numbers.
- Use only the supplied forecast.
- Be concise and professional.
- Use markdown headings and bullet points.
- Keep the response under 500 words.
"""

    try:

        response = MODEL.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        return (
            "Gemini AI Error:\n\n"
            f"{e}"
        )