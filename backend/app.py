import os
from flask      import Flask, jsonify, request
from flask_cors  import CORS
from dotenv      import load_dotenv
from analyzer    import analyze_file
from ai_analyzer import analyze_with_ai

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'لم يتم إرسال ملف'}), 400

    file = request.files['file']

    if not file.filename.endswith('.py'):
        return jsonify({'error': 'الملف يجب أن يكون .py'}), 400

    # حفظ الملف
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 1. تحليل الأدوات الثلاثة (من الأسبوع الثالث)
    static_report = analyze_file(filepath)

    # 2. قراءة محتوى الكود لإرساله لـ Gemini
    with open(filepath, 'r', encoding='utf-8') as f:
        code_content = f.read()

    # 3. تحليل Gemini AI
    ai_report = analyze_with_ai(code_content, static_report)

    # 4. دمج كل شيء في تقرير واحد
    full_report = {
        **static_report,        # pylint + flake8 + bandit + summary
        'ai_analysis': ai_report
    }

    return jsonify(full_report)


if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)