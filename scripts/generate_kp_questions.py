import sqlite3
import json
import os
import time
import requests

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "408_study.db")
# Put your DashScope API key here or set the environment variable DASHSCOPE_API_KEY
API_KEY = os.getenv("DASHSCOPE_API_KEY", "YOUR_API_KEY_HERE")
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def call_qwen(prompt):
    """Call qwen3.6-plus via DashScope API."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen3.6-plus",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        # Remove markdown code blocks if present
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"API Error: {e}")
        return None

def generate_questions_for_kp(kp_id, kp_name, subject_name, chapter_name, content):
    """Generate questions for a single knowledge point."""
    prompt = f"""
你是一个专业的408计算机考研命题专家。请根据以下知识点生成题目。

知识点层级：{subject_name} -> {chapter_name} -> {kp_name}
知识点内容：{content if content else '无详细描述，请根据通用计算机考研大纲生成'}

请生成 3 道题目：
1. 2道单项选择题（包含A/B/C/D选项）
2. 1道简答题/名词解释

必须返回严格的 JSON 格式数组（不要包含任何其他解释性文字）：
[
  {{
    "type": "multiple_choice",
    "question": "题干内容",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "正确选项字母",
    "explanation": "详细解析"
  }},
  {{
    "type": "short_answer",
    "question": "简答题题干",
    "options": null,
    "answer": "标准答案核心点",
    "explanation": "详细解析"
  }}
]
"""
    return call_qwen(prompt)

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ 请先在脚本开头设置 DASHSCOPE_API_KEY 环境变量或修改 API_KEY 变量")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all knowledge points with hierarchy context
    cursor.execute("""
        SELECT kp.id, kp.name, kp.content, s.name as subject, ch.name as chapter 
        FROM knowledge_points kp 
        JOIN chapters ch ON kp.chapter_id = ch.id 
        JOIN subjects s ON ch.subject_id = s.id
        ORDER BY s.name, ch.name, kp.order_index
    """)
    kps = cursor.fetchall()

    total = len(kps)
    generated_count = 0

    print(f"🚀 开始为 {total} 个知识点生成题目...")

    for i, kp in enumerate(kps):
        kp_id = kp['id']
        kp_name = kp['name']
        
        # Check if questions already exist
        cursor.execute("SELECT count(*) as cnt FROM questions WHERE knowledge_point_id = ?", (kp_id,))
        existing = cursor.fetchone()['cnt']
        
        if existing >= 3:
            print(f"[{i+1}/{total}] 跳过 {kp_name} (已有 {existing} 题)")
            continue
            
        print(f"[{i+1}/{total}] 生成 {kp_name} ...")
        
        questions = generate_questions_for_kp(kp_id, kp_name, kp['subject'], kp['chapter'], kp['content'])
        
        if questions:
            try:
                for q in questions:
                    q_type = q.get("type", "short_answer")
                    # Map type to db schema if needed
                    db_type = q_type
                    
                    options = json.dumps(q.get("options")) if q.get("options") else None
                    
                    cursor.execute("""
                        INSERT INTO questions (knowledge_point_id, type, question, options, answer, explanation, difficulty, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, 3, datetime('now'))
                    """, (
                        kp_id, 
                        db_type, 
                        q.get("question"), 
                        options, 
                        q.get("answer"), 
                        q.get("explanation")
                    ))
                conn.commit()
                generated_count += 1
                print(f"  ✅ 成功插入 {len(questions)} 题")
            except Exception as e:
                print(f"  ❌ 数据库错误: {e}")
        else:
            print(f"  ❌ 生成失败")
        
        # Rate limit protection
        time.sleep(1.5)

    conn.close()
    print(f"\n🎉 完成！共为 {generated_count} 个知识点生成了题目。")

if __name__ == "__main__":
    main()