import subprocess
import json
import os

def run_pylint(filepath: str) -> dict:
    """تشغيل pylint على الملف وإرجاع النتائج كـ dict"""

    try:
        result = subprocess.run(
            ['pylint', filepath,
             '--output-format=json',   # نتائج بصيغة JSON
             '--score=yes'],            # نريد النقاط
            capture_output=True,
            text=True
        )

        # pylint يكتب النتائج في stdout
        issues = json.loads(result.stdout) if result.stdout.strip() else []

        # استخراج النقاط من stderr
        score = 0.0
        for line in result.stderr.splitlines():
            if 'rated at' in line:
                # مثال: "Your code has been rated at 7.5/10"
                score = float(line.split('rated at ')[1].split('/')[0])

        return {
            'tool': 'pylint',
            'score': score,
            'issues_count': len(issues),
            'issues': issues
        }

    except Exception as e:
        return {'tool': 'pylint', 'error': str(e)}
        
        
def run_flake8(filepath: str) -> dict:
    """تشغيل flake8 للتحقق من معايير PEP8"""
    try:
        result = subprocess.run(
            ['flake8', filepath,
             '--format=%(row)d:%(col)d:%(code)s:%(text)s'],
            capture_output=True,
            text=True
        )

        issues = []
        for line in result.stdout.strip().splitlines():
            if line:
                parts = line.split(':', 3)
                if len(parts) == 4:
                    issues.append({
                        'line':    int(parts[0]),
                        'col':     int(parts[1]),
                        'code':    parts[2],
                        'message': parts[3]
                    })

        return {
            'tool': 'flake8',
            'issues_count': len(issues),
            'issues': issues
        }

    except Exception as e:
        return {'tool': 'flake8', 'error': str(e)}
        
        
def run_bandit(filepath: str) -> dict:
    """تشغيل bandit للكشف عن الثغرات الأمنية"""

    try:
        result = subprocess.run(
            ['bandit', filepath, '-f', 'json', '-q'],
            capture_output=True,
            text=True
        )

        data = json.loads(result.stdout) if result.stdout.strip() else {}
        results = data.get('results', [])

        # تصنيف المشاكل حسب الخطورة
        high   = [i for i in results if i['issue_severity'] == 'HIGH']
        medium = [i for i in results if i['issue_severity'] == 'MEDIUM']
        low    = [i for i in results if i['issue_severity'] == 'LOW']

        return {
            'tool':         'bandit',
            'issues_count': len(results),
            'high':         high,
            'medium':       medium,
            'low':          low
        }

    except Exception as e:
        return {'tool': 'bandit', 'error': str(e)}
        

def analyze_file(filepath: str) -> dict:
    """تشغيل كل الأدوات ودمج النتائج في تقرير واحد"""

    pylint_result = run_pylint(filepath)
    flake8_result = run_flake8(filepath)
    bandit_result = run_bandit(filepath)

    return {
        'filename':  os.path.basename(filepath),
        'pylint':    pylint_result,
        'flake8':    flake8_result,
        'bandit':    bandit_result,
        'summary': {
            'quality_score':    pylint_result.get('score', 0),
            'style_issues':     flake8_result.get('issues_count', 0),
            'security_issues':  bandit_result.get('issues_count', 0)
        }
    }





