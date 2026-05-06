# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import time
import urllib.request
import urllib.error
import sys
from datetime import datetime

# Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "408_study.db")
API_KEY = os.getenv("DASHSCOPE_API_KEY", "YOUR_API_KEY_HERE")
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def call_qwen(prompt):
    """Call qwen3.6-plus via DashScope API using urllib."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "model": "qwen3.6-plus",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }).encode('utf-8')
    
    # Retry logic with increased timeout (120s)
    for attempt in range(3):
        try:
            req = urllib.request.Request(API_URL, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode('utf-8'))
                content = data["choices"][0]["message"]["content"]
                # Remove markdown code blocks if present
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
        except urllib.error.URLError as e:
            print(f"  [Network] Timeout or error (attempt {attempt+1}/3): {e}", flush=True)
            if attempt < 2:
                time.sleep(3) # Wait before retry
        except Exception as e:
            print(f"  [Error] API Error: {e}", flush=True)
            return None
    return None

def main():
    print("408 知识点题目生成脚本启动", flush=True)
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please set DASHSCOPE_API_KEY environment variable", flush=True)
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Get total KPs
    cursor.execute("SELECT count(*) as total FROM knowledge_points")
    total_kps = cursor.fetchone()['total']
    
    # 2. Scan for pending KPs (less than 3 questions)
    print("Scanning database for pending topics...", flush=True)
    
    cursor.execute("""
        SELECT kp.id, kp.name, kp.content, s.name as subject, ch.name as chapter 
        FROM knowledge_points kp 
        JOIN chapters ch ON kp.chapter_id = ch.id 
        JOIN subjects s ON ch.subject_id = s.id
        ORDER BY s.name, ch.name, kp.order_index
    """)
    kps = cursor.fetchall()

    pending_kps = []
    for kp in kps:
        cursor.execute("SELECT count(*) as cnt FROM questions WHERE knowledge_point_id = ?", (kp['id'],))
        existing = cursor.fetchone()['cnt']
        if existing < 3:
            pending_kps.append(kp)
    
    work_needed = len(pending_kps)
    print(f"Found {work_needed} topics needing questions (out of {total_kps} total)", flush=True)

    if work_needed == 0:
        print("All topics have enough questions. Done!")
        return

    # Start processing
    start_time = time.time()
    generated_count = 0
    
    print(f"Starting generation...", flush=True)

    for i, kp in enumerate(pending_kps):
        kp_id = kp['id']
        kp_name = kp['name']
        
        # Dynamic ETA calculation
        elapsed = time.time() - start_time
        if generated_count > 0:
            avg_time_per_kp = elapsed / generated_count
            remaining = work_needed - generated_count
            eta_seconds = remaining * avg_time_per_kp
            eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
        else:
            eta_str = "Calculating..."

        print(f"[{i+1}/{work_needed}] Generating: {kp_name} (ETA: {eta_str})", flush=True)
        
        # Generate prompt
        prompt = f"""
You are an expert exam setter for the 408 Computer Science Graduate Entrance Exam.
Please generate questions based on the following knowledge point.

Hierarchy: {kp['subject']} -> {kp['chapter']} -> {kp_name}
Content: {kp['content'] if kp['content'] else 'General knowledge based on syllabus'}

Generate exactly 3 questions:
1. Two multiple-choice questions (with options A, B, C, D).
2. One short-answer/definition question.

Return a STRICT JSON array:
[
  {{
    "type": "multiple_choice",
    "question": "Question text",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "Correct Option Letter",
    "explanation": "Detailed explanation"
  }},
  {{
    "type": "short_answer",
    "question": "Question text",
    "options": null,
    "answer": "Core answer points",
    "explanation": "Detailed explanation"
  }}
]
"""
        questions = call_qwen(prompt)
        
        if questions:
            try:
                for q in questions:
                    q_type = q.get("type", "short_answer")
                    options_obj = q.get("options")
                    options_str = json.dumps(options_obj) if options_obj else "{}"
                    
                    explanation = q.get("explanation")
                    if isinstance(explanation, list):
                        explanation = " ".join(explanation)
                    
                    cursor.execute("""
                        INSERT INTO questions (knowledge_point_id, type, question, options, answer, explanation, difficulty, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, 3, datetime('now'))
                    """, (
                        kp_id, 
                        q_type, 
                        q.get("question"), 
                        options_str, 
                        q.get("answer"), 
                        explanation
                    ))
                conn.commit()
                generated_count += 1
                print(f"  Success: Inserted {len(questions)} questions (Total: {generated_count})", flush=True)
                
                # Progress Report every 10
                if generated_count % 10 == 0:
                    current_avg = elapsed / generated_count
                    remaining = work_needed - generated_count
                    eta_secs = remaining * current_avg
                    print(f"\n>> PROGRESS REPORT: Completed {generated_count} topics. Avg {current_avg:.1f}s/topic. Est remaining: {eta_secs:.0f}s ({eta_secs/60:.1f} mins)\n", flush=True)

            except Exception as e:
                print(f"  DB Error: {e}", flush=True)
        else:
            print(f"  Failed to generate", flush=True)
        
        # Rate limit
        time.sleep(1.5)

    conn.close()
    total_elapsed = time.time() - start_time
    print(f"\nDone! Generated questions for {generated_count} topics. Total time: {total_elapsed:.1f}s", flush=True)

if __name__ == "__main__":
    main()