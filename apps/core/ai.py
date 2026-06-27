import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def ask_qwen(prompt: str, system: str = "", model: str = None) -> str:
    api_key = getattr(settings, 'QWEN_API_KEY', '')
    if not api_key:
        return ""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url=getattr(settings, 'QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
        )
        resp = client.chat.completions.create(
            model=model or getattr(settings, 'QWEN_MODEL', 'qwen-turbo'),
            messages=[
                {"role": "system", "content": system or "Ты помощник IT-отдела компании. Отвечай кратко и по делу на русском языке."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=800,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Qwen AI error: {e}")
        return ""


def generate_weekly_summary(exp_lic: int, exp_dom: int, exp_isp: int) -> str:
    prompt = f"""
Данные IT-реестра компании (горизонт 90 дней):
- Лицензий истекает: {exp_lic}
- Доменов истекает: {exp_dom}
- Договоров с провайдерами истекает: {exp_isp}

Напиши управленческую сводку: 3-4 коротких предложения с приоритетами и рекомендациями на эту неделю.
Если всё в порядке — скажи это позитивно. Интерпретируй цифры, не просто их перечисляй.
"""
    return ask_qwen(prompt)


def search_assets(query: str, context: str) -> str:
    prompt = f"""
Данные IT-реестра:
{context}

Запрос пользователя: "{query}"

Найди и перечисли релевантные записи. Дай краткий структурированный ответ на русском языке.
Используй • для элементов списка. Максимум 15 строк.
Если ничего не найдено — напиши: "Ничего не найдено по запросу."
"""
    return ask_qwen(prompt)


def suggest_category(app_name: str, vendor_name: str = "") -> str:
    valid = ['erp', 'hr', 'bi', 'mining', 'cad', 'office', 'security', 'legal', 'other']
    prompt = f"""
Определи категорию IT-приложения.
Название: "{app_name}"
Вендор: "{vendor_name or 'не указан'}"

Категории (верни только код без пояснений):
erp — ERP / Бухгалтерия (1С, SAP, Oracle ERP)
hr — HR / Зарплата (кадровые системы)
bi — BI / Аналитика (отчётность, дашборды, Power BI)
mining — Горное ПО (специализированный горнодобывающий软件)
cad — САПР (AutoCAD, проектирование)
office — Офисный пакет (MS Office, почта, Teams)
security — Безопасность (антивирус, VPN, DLP)
legal — Правовая база (КонсультантПлюс)
other — Другое

Ответь ТОЛЬКО кодом категории.
"""
    raw = ask_qwen(prompt).strip().lower()
    result = raw.split()[0] if raw else "other"
    return result if result in valid else "other"
