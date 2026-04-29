import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')


def build_prompt(code: str, static_report: dict) -> str:

    score    = static_report['pylint'].get('score', 0)
    issues   = static_report['pylint'].get('issues', [])[:5]
    f8_count = static_report['flake8'].get('issues_count', 0)
    high     = len(static_report['bandit'].get('high', []))
    medium   = len(static_report['bandit'].get('medium', []))

    issues_text = "\n".join(
        f"  - Line {i['line']}: {i['message']}" for i in issues
    ) or "  - No issues found"

    return f"""# Role
You are a professional Python code reviewer. Your job is to add value 
BEYOND what static analysis tools already found.

# Static Analysis Results (context only — do not repeat these)
- Code quality score (pylint): {score}/10
- Style violations (flake8): {f8_count} issues
- Security vulnerabilities (bandit): {high} high, {medium} medium
- Top issues already detected:
{issues_text}

# Code to Review
```python
{code}
```

# Your Task
Provide a structured review with ONLY these sections:

## Summary
Two sentences maximum: overall code quality and the single most 
important improvement needed.

## Top 3 Issues to Fix
For each issue:
- Line number
- Why it is a problem
- Concrete fix with example

## Improved Code Snippet
Rewrite ONLY the most problematic part — not the entire file.

# Rules
- Do NOT repeat what the static tools already reported
- Do NOT praise obvious things
- Do NOT add generic advice that applies to every Python file
- If the code is good, say so clearly and briefly
- Be direct and specific — every sentence must add value
- IMPORTANT: Write your entire response in Arabic"""

def analyze_with_ai(code: str, static_report: dict) -> dict:
    try:
        prompt   = build_prompt(code, static_report)
        response = model.generate_content(prompt)
        return {
            'success':  True,
            'analysis': response.text,
            'model':    'gemini-2.5-flash'
        }
    except Exception as e:
        return {
            'success':  False,
            'error':    str(e),
            'analysis': 'تعذّر الاتصال بـ Gemini API'
        }