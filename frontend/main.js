
// ── المتغيرات ──────────────────────────────
const uploadArea  = document.getElementById('uploadArea')
const fileInput   = document.getElementById('fileInput')
const fileName    = document.getElementById('fileName')
const analyzeBtn  = document.getElementById('analyzeBtn')
const loading     = document.getElementById('loading')
const report      = document.getElementById('report')
const errorMsg    = document.getElementById('errorMsg')
let   selectedFile = null

// ── أحداث منطقة الرفع ─────────────────────
uploadArea.addEventListener('click', () => fileInput.click())

fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (!file.name.endsWith('.py')) {
    showError('يرجى اختيار ملف .py فقط'); return
  }
  selectedFile = file
  fileName.textContent = '✓ ' + file.name
  analyzeBtn.disabled = false
  analyzeBtn.textContent = 'تحليل الكود بـ AI'
  errorMsg.style.display = 'none'
  report.style.display = 'none'
})

// ── إرسال الملف ───────────────────────────
analyzeBtn.addEventListener('click', async () => {
  if (!selectedFile) return

  // إظهار loading
  analyzeBtn.disabled = true
  loading.style.display = 'block'
  report.style.display  = 'none'
  errorMsg.style.display = 'none'

  const formData = new FormData()
  formData.append('file', selectedFile)

  try {
    const res  = await fetch('http://localhost:5000/analyze', {
      method: 'POST', body: formData
    })
    const data = await res.json()

    loading.style.display = 'none'
    renderReport(data)

  } catch (err) {
    loading.style.display = 'none'
    showError('تعذّر الاتصال بالسيرفر — تأكد أن Flask يعمل على port 5000')
  } finally {
    analyzeBtn.disabled = false
    analyzeBtn.textContent = 'تحليل مرة أخرى'
  }
})

// ── بناء التقرير ──────────────────────────
function renderReport(data) {
  let html = ''

  // بطاقات الملخص
  html += `
  <div class="summary-grid">
    <div class="summary-card green">
      <span class="num">${data.summary.quality_score}</span>
      <span class="lbl">جودة الكود / 10</span>
    </div>
    <div class="summary-card amber">
      <span class="num">${data.summary.style_issues}</span>
      <span class="lbl">مشاكل Style</span>
    </div>
    <div class="summary-card red">
      <span class="num">${data.summary.security_issues}</span>
      <span class="lbl">تحذيرات أمنية</span>
    </div>
  </div>`

  // تحليل Gemini AI

if (data.ai_analysis?.success) {
    html += `
    <div class="ai-section">
      <h3>🤖 تحليل Gemini AI</h3>
      <div class="ai-content">${escapeHtml(data.ai_analysis.analysis)}</div>
    </div>`
} else {
    html += `
    <div class="ai-section">
      <h3>🤖 تحليل Gemini AI</h3>
      <div class="ai-content" style="color:#ef4444;">
        ⚠️ ${escapeHtml(data.ai_analysis?.error || 'خطأ غير معروف')}
      </div>
    </div>`
}

  // مشاكل pylint
  html += `<div class="section"><h3>🔍 نتائج pylint</h3>`
  if (data.pylint.issues?.length) {
    data.pylint.issues.forEach(i => {
      html += `<div class="issue-item">
        <span class="line-badge">سطر ${i.line}</span>
        <span>${escapeHtml(i.message)}</span>
      </div>`
    })
  } else {
    html += `<p class="no-issues">✓ لا توجد مشاكل</p>`
  }
  html += `</div>`

  // تحذيرات bandit
  html += `<div class="section"><h3>🔒 التحذيرات الأمنية</h3>`
  const secIssues = [...(data.bandit.high||[]), ...(data.bandit.medium||[])]
  if (secIssues.length) {
    secIssues.forEach(i => {
      const cls = i.issue_severity === 'HIGH' ? 'sev-high' : 'sev-medium'
      html += `<div class="issue-item">
        <span class="line-badge">سطر ${i.line_number}</span>
        <span class="${cls}">${escapeHtml(i.issue_text)}</span>
      </div>`
    })
  } else {
    html += `<p class="no-issues">✓ لا توجد تحذيرات أمنية</p>`
  }
  html += `</div>`

  report.innerHTML = html
  report.style.display = 'block'
  report.scrollIntoView({ behavior: 'smooth' })
}

// ── دوال مساعدة ───────────────────────────
function showError(msg) {
  errorMsg.textContent = msg
  errorMsg.style.display = 'block'
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}