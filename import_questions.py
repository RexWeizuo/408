import re
import json
import os
import httpx
import asyncio

# Configuration
OCR_DIR = r"d:\study\408\wd练习题_文本_OCR"
API_BASE = "http://localhost:8000"

# Subject/chapter mapping from syllabus_structure.json
SUBJECTS = {
    "computer_network": {
        "name": "计算机网络",
        "file": "27计网选择题刷题本.txt",
        "chapters": {
            "cn_ch1": "计算机网络体系结构|计算机网络概述|体系结构|参考模型|网络模型",
            "cn_ch2": "物理层|通信基础|传输介质|物理层设备|信道|编码|调制|电路交换|报文交换|分组交换",
            "cn_ch3": "数据链路层|组帧|差错控制|流量控制|可靠传输|介质访问控制|局域网|广域网|CSMA|以太网|VLAN|PPP",
            "cn_ch4": "网络层|IP|IPv4|IPv6|路由|RIP|OSPF|BGP|ARP|DHCP|ICMP|CIDR|NAT|子网|路由器",
            "cn_ch5": "传输层|UDP|TCP|端口|拥塞控制|流量控制|可靠传输|连接管理",
            "cn_ch6": "应用层|DNS|FTP|电子邮件|SMTP|POP3|HTTP|WWW|客户服务器|P2P",
        }
    },
    "operating_system": {
        "name": "操作系统",
        "file": "27操作系统选择题刷题本.txt",
        "chapters": {
            "os_ch1": "操作系统概述|基本概念|发展历程|运行环境|中断|异常|系统调用|虚拟机",
            "os_ch2": "进程|线程|CPU调度|同步与互斥|死锁|信号量|管程|互斥锁|条件变量",
            "os_ch3": "内存管理|虚拟内存|页式|段式|连续分配|页置换|TLB|请求分页",
            "os_ch4": "文件|目录|inode|文件系统|硬链接|软链接|文件系统",
            "os_ch5": "I/O|输入输出|设备|磁盘|缓冲区|SPOOLing|驱动程序",
        }
    },
    "data_structure": {
        "name": "数据结构",
        "file": "27wd数据结构选择题刷题本.txt",
        "chapters": {
            "ds_ch1": "绪论|基本概念|算法|复杂度|时间复杂度|空间复杂度",
            "ds_ch2": "线性表|顺序表|链表|单链表|双链表|循环链表",
            "ds_ch3": "栈|队列|数组|多维数组|特殊矩阵|压缩存储",
            "ds_ch4": "树|二叉树|遍历|线索|哈夫曼|并查集|堆",
            "ds_ch5": "图|邻接|遍历|生成树|最短路径|拓扑排序|关键路径",
            "ds_ch6": "查找|顺序查找|折半查找|二叉搜索树|平衡二叉树|B树|B+树|散列表|哈希",
            "ds_ch7": "排序|插入排序|冒泡|选择排序|快速排序|堆排序|归并排序|基数排序|外部排序",
        }
    },
    "computer_organization": {
        "name": "计算机组成原理",
        "file": "27wd计组选择题刷题本.txt",
        "chapters": {
            "co_ch1": "计算机系统概述|基本组成|硬件结构|性能指标|冯·诺依曼",
            "co_ch2": "数据|运算|补码|浮点数|IEEE 754|定点数|ALU|加减乘除",
            "co_ch3": "存储器|Cache|虚拟存储器|SRAM|DRAM|磁盘|SSD|映射|替换算法",
            "co_ch4": "指令|寻址|指令格式|CISC|RISC|机器级代码",
            "co_ch5": "CPU|处理器|指令流水线|数据通路|控制器|中断|异常|超标量",
            "co_ch6": "总线|输入输出|I/O|中断|DMA|程序查询",
        }
    }
}

# Knowledge points per chapter (from syllabus_structure.json)
KP_MAPPING = {
    "cn_ch1": ["cn_ch1_1", "cn_ch1_2", "cn_ch1_3", "cn_ch1_4", "cn_ch1_5", "cn_ch1_6"],
    "cn_ch2": ["cn_ch2_1", "cn_ch2_2", "cn_ch2_3", "cn_ch2_4", "cn_ch2_5", "cn_ch2_6", "cn_ch2_7", "cn_ch2_8"],
    "cn_ch3": ["cn_ch3_1", "cn_ch3_2", "cn_ch3_3", "cn_ch3_4", "cn_ch3_5", "cn_ch3_6", "cn_ch3_7", "cn_ch3_8", "cn_ch3_9", "cn_ch3_10", "cn_ch3_11", "cn_ch3_12", "cn_ch3_13", "cn_ch3_14", "cn_ch3_15", "cn_ch3_16", "cn_ch3_17", "cn_ch3_18"],
    "cn_ch4": ["cn_ch4_1", "cn_ch4_2", "cn_ch4_3", "cn_ch4_4", "cn_ch4_5", "cn_ch4_6", "cn_ch4_7", "cn_ch4_8", "cn_ch4_9", "cn_ch4_10", "cn_ch4_11", "cn_ch4_12", "cn_ch4_13", "cn_ch4_14", "cn_ch4_15", "cn_ch4_16", "cn_ch4_17", "cn_ch4_18", "cn_ch4_19", "cn_ch4_20"],
    "cn_ch5": ["cn_ch5_1", "cn_ch5_2", "cn_ch5_3", "cn_ch5_4", "cn_ch5_5", "cn_ch5_6", "cn_ch5_7", "cn_ch5_8", "cn_ch5_9"],
    "cn_ch6": ["cn_ch6_1", "cn_ch6_2", "cn_ch6_3", "cn_ch6_4", "cn_ch6_5", "cn_ch6_6", "cn_ch6_7"],
    "os_ch1": ["os_ch1_1", "os_ch1_2", "os_ch1_3", "os_ch1_4", "os_ch1_5", "os_ch1_6", "os_ch1_7", "os_ch1_8", "os_ch1_9", "os_ch1_10"],
    "os_ch2": ["os_ch2_1", "os_ch2_2", "os_ch2_3", "os_ch2_4", "os_ch2_5", "os_ch2_6", "os_ch2_7", "os_ch2_8", "os_ch2_9", "os_ch2_10", "os_ch2_11", "os_ch2_12", "os_ch2_13", "os_ch2_14", "os_ch2_15", "os_ch2_16", "os_ch2_17", "os_ch2_18", "os_ch2_19", "os_ch2_20"],
    "os_ch3": ["os_ch3_1", "os_ch3_2", "os_ch3_3", "os_ch3_4", "os_ch3_5", "os_ch3_6", "os_ch3_7", "os_ch3_8", "os_ch3_9", "os_ch3_10", "os_ch3_11"],
    "os_ch4": ["os_ch4_1", "os_ch4_2", "os_ch4_3", "os_ch4_4", "os_ch4_5", "os_ch4_6", "os_ch4_7", "os_ch4_8", "os_ch4_9", "os_ch4_10", "os_ch4_11", "os_ch4_12", "os_ch4_13", "os_ch4_14"],
    "os_ch5": ["os_ch5_1", "os_ch5_2", "os_ch5_3", "os_ch5_4", "os_ch5_5", "os_ch5_6", "os_ch5_7", "os_ch5_8", "os_ch5_9", "os_ch5_10", "os_ch5_11", "os_ch5_12"],
    "ds_ch1": ["ds_ch1_1", "ds_ch1_2"],
    "ds_ch2": ["ds_ch2_1", "ds_ch2_2", "ds_ch2_3", "ds_ch2_4"],
    "ds_ch3": ["ds_ch3_1", "ds_ch3_2", "ds_ch3_3", "ds_ch3_4", "ds_ch3_5", "ds_ch3_6"],
    "ds_ch4": ["ds_ch4_1", "ds_ch4_2", "ds_ch4_3", "ds_ch4_4", "ds_ch4_5", "ds_ch4_6", "ds_ch4_7", "ds_ch4_8", "ds_ch4_9", "ds_ch4_10", "ds_ch4_11"],
    "ds_ch5": ["ds_ch5_1", "ds_ch5_2", "ds_ch5_3", "ds_ch5_4", "ds_ch5_5", "ds_ch5_6", "ds_ch5_7", "ds_ch5_8", "ds_ch5_9", "ds_ch5_10"],
    "ds_ch6": ["ds_ch6_1", "ds_ch6_2", "ds_ch6_3", "ds_ch6_4", "ds_ch6_5", "ds_ch6_6", "ds_ch6_7", "ds_ch6_8", "ds_ch6_9", "ds_ch6_10", "ds_ch6_11", "ds_ch6_12"],
    "ds_ch7": ["ds_ch7_1", "ds_ch7_2", "ds_ch7_3", "ds_ch7_4", "ds_ch7_5", "ds_ch7_6", "ds_ch7_7", "ds_ch7_8", "ds_ch7_9", "ds_ch7_10", "ds_ch7_11", "ds_ch7_12"],
    "co_ch1": ["co_ch1_1", "co_ch1_2", "co_ch1_3", "co_ch1_4", "co_ch1_5"],
    "co_ch2": ["co_ch2_1", "co_ch2_2", "co_ch2_3", "co_ch2_4", "co_ch2_5", "co_ch2_6", "co_ch2_7", "co_ch2_8", "co_ch2_9"],
    "co_ch3": ["co_ch3_1", "co_ch3_2", "co_ch3_3", "co_ch3_4", "co_ch3_5", "co_ch3_6", "co_ch3_7", "co_ch3_8", "co_ch3_9", "co_ch3_10", "co_ch3_11", "co_ch3_12", "co_ch3_13", "co_ch3_14", "co_ch3_15", "co_ch3_16", "co_ch3_17", "co_ch3_18"],
    "co_ch4": ["co_ch4_1", "co_ch4_2", "co_ch4_3", "co_ch4_4", "co_ch4_5", "co_ch4_6"],
    "co_ch5": ["co_ch5_1", "co_ch5_2", "co_ch5_3", "co_ch5_4", "co_ch5_5", "co_ch5_6", "co_ch5_7", "co_ch5_8", "co_ch5_9", "co_ch5_10", "co_ch5_11", "co_ch5_12"],
    "co_ch6": ["co_ch6_1", "co_ch6_2", "co_ch6_3", "co_ch6_4", "co_ch6_5", "co_ch6_6", "co_ch6_7", "co_ch6_8"],
}


def read_ocr_file(filepath):
    """Read the OCR text file and return raw content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def determine_chapter(line_text, chapter_patterns):
    """Determine which chapter a line belongs to based on keyword matching."""
    for ch_id, pattern in chapter_patterns.items():
        if re.search(pattern, line_text):
            return ch_id
    return None


def extract_questions_from_text(text, chapter_patterns):
    """Extract individual questions from OCR text."""
    # Remove page separators and headers
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('===') or line.startswith('---') or '本资料仅供内部学习使用' in line:
            continue
        if '27' in line and '刷题本' in line and '仅作学习交流使用' in line:
            continue
        if re.match(r'^\d+$', line) and len(line) <= 4:
            continue
        cleaned_lines.append(line)

    # Find questions - each starts with a number followed by . or 、
    questions = []
    current_question = None
    current_chapter = None
    current_section = None

    # Pattern for question number: e.g., "1.", "1.【2010统考真题】", "7.不同的数据交换方式"
    question_pattern = re.compile(r'^(\d+)\.[【\.．、]?(.*)')

    # Pattern for options: e.g., "A.", "B.", "C.", "D."
    option_pattern = re.compile(r'^([A-D])[\.．、：:\s](.*)')

    # Pattern for chapter/section headers
    chapter_header_pattern = re.compile(r'^(第[一二三四五六七八九十]章|[0-9]+[\.．][0-9]+)\s*(.*)')

    for i, line in enumerate(cleaned_lines):
        # Check for chapter/section headers
        ch_match = chapter_header_pattern.match(line)
        if ch_match:
            detected_ch = determine_chapter(line, chapter_patterns)
            if detected_ch:
                current_chapter = detected_ch
            continue

        # Check for question start
        q_match = question_pattern.match(line)
        if q_match:
            q_num = int(q_match.group(1))
            q_text = q_match.group(2)
            
            # Skip non-question items like directory pages
            if q_num > 0 and q_num < 200:
                current_question = {
                    'number': q_num,
                    'question': q_text,
                    'options': {},
                    'chapter': current_chapter,
                    'answer': '',
                    'explanation': '',
                }
                questions.append(current_question)
                continue

        # If we have a current question, check if this line is an option or continuation
        if current_question is not None:
            opt_match = option_pattern.match(line)
            if opt_match:
                opt_letter = opt_match.group(1)
                opt_text = opt_match.group(2).strip()
                current_question['options'][opt_letter] = opt_text
            elif line and current_question['question']:
                # Could be continuation of question or options
                # If it looks like an option without letter prefix
                if re.match(r'^[A-D][\.．、：:\s]', line):
                    pass  # Already handled above
                else:
                    # Append to last option or question
                    if current_question['options']:
                        last_opt = list(current_question['options'].keys())[-1]
                        current_question['options'][last_opt] += line
                    else:
                        current_question['question'] += line

    # Clean up questions - remove incomplete ones
    valid_questions = []
    for q in questions:
        if len(q['options']) >= 2 and len(q['question'].strip()) > 5:
            # Clean up the question text
            q['question'] = re.sub(r'\s+', '', q['question'].strip())
            for k, v in q['options'].items():
                q['options'][k] = re.sub(r'\s+', '', v.strip())
            valid_questions.append(q)

    return valid_questions


def determine_knowledge_point(question_text, chapter_id):
    """Determine the best knowledge point for a question based on content."""
    kp_ids = KP_MAPPING.get(chapter_id, [])
    if not kp_ids:
        return None
    
    # Simple heuristic: use the first KP in the chapter
    # For more accurate mapping, we'd need NLP or manual tagging
    return kp_ids[0]


async def check_server_running():
    """Check if the FastAPI server is running."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_BASE}/", timeout=10.0)
            return resp.status_code == 200
    except Exception as e:
        print(f"Server check failed: {e}")
        return False


async def create_question(client, question_data):
    """Create a question via the API."""
    try:
        resp = await client.post(f"{API_BASE}/api/questions/", json=question_data, timeout=10.0)
        if resp.status_code == 200:
            return True, resp.json().get('id')
        else:
            return False, resp.text
    except Exception as e:
        return False, str(e)


async def main():
    checklist = []
    total_stats = {"success": 0, "failed": 0, "skipped": 0}

    # Check if server is running
    server_running = await check_server_running()
    print(f"Server running: {server_running}")

    if server_running:
        async with httpx.AsyncClient() as api_client:
            for subject_id, subject_info in SUBJECTS.items():
                filepath = os.path.join(OCR_DIR, subject_info['file'])
                if not os.path.exists(filepath):
                    print(f"File not found: {filepath}")
                    checklist.append({
                        'subject': subject_info['name'],
                        'status': 'skipped',
                        'reason': f'File not found: {subject_info["file"]}'
                    })
                    total_stats['skipped'] += 1
                    continue

                print(f"\n{'='*60}")
                print(f"Processing: {subject_info['name']}")
                print(f"{'='*60}")

                text = read_ocr_file(filepath)
                questions = extract_questions_from_text(text, subject_info['chapters'])
                print(f"Found {len(questions)} questions")

                # Filter out questions where chapter couldn't be determined
                uncategorized = [q for q in questions if not q['chapter']]
                categorized = [q for q in questions if q['chapter']]
                
                if uncategorized:
                    print(f"Uncategorized: {len(uncategorized)} questions (no chapter match)")
                    for q in uncategorized:
                        checklist.append({
                            'subject': subject_info['name'],
                            'number': q['number'],
                            'status': 'failed',
                            'reason': '未匹配到章节',
                            'question_preview': q['question'][:50]
                        })
                        total_stats['failed'] += 1

                # Process categorized questions
                for q in categorized:
                    kp_id = determine_knowledge_point(q['question'], q['chapter'])
                    if not kp_id:
                        checklist.append({
                            'subject': subject_info['name'],
                            'chapter': q['chapter'],
                            'number': q['number'],
                            'status': 'failed',
                            'reason': '未找到知识点ID',
                            'question_preview': q['question'][:50]
                        })
                        total_stats['failed'] += 1
                        continue

                    options_list = [
                        f"A. {q['options'].get('A', '')}",
                        f"B. {q['options'].get('B', '')}",
                        f"C. {q['options'].get('C', '')}",
                        f"D. {q['options'].get('D', '')}",
                    ]

                    question_data = {
                        'knowledge_point_id': kp_id,
                        'type': 'choice',
                        'question': q['question'],
                        'options': options_list,
                        'answer': q.get('answer', '') or '',
                        'explanation': q.get('explanation', '') or '',
                        'difficulty': 1,
                    }

                    if server_running:
                        success, result = await create_question(api_client, question_data)
                        if success:
                            checklist.append({
                                'subject': subject_info['name'],
                                'chapter': q['chapter'],
                                'number': q['number'],
                                'status': 'success',
                                'kp_id': kp_id,
                                'question_preview': q['question'][:50],
                                'api_id': result
                            })
                            total_stats['success'] += 1
                        else:
                            checklist.append({
                                'subject': subject_info['name'],
                                'chapter': q['chapter'],
                                'number': q['number'],
                                'status': 'failed',
                                'reason': f'API error: {result}',
                                'question_preview': q['question'][:50]
                            })
                            total_stats['failed'] += 1
                    else:
                        checklist.append({
                            'subject': subject_info['name'],
                            'chapter': q['chapter'],
                            'number': q['number'],
                            'status': 'ready',
                            'kp_id': kp_id,
                            'question_preview': q['question'][:50]
                        })
                        total_stats['success'] += 1

    # Save checklist
    checklist_path = r"d:\study\408\wd练习题_导入清单.json"
    with open(checklist_path, 'w', encoding='utf-8') as f:
        json.dump({
            'stats': total_stats,
            'questions': checklist
        }, f, ensure_ascii=False, indent=2)

    # Generate human-readable report
    report_path = r"d:\study\408\wd练习题_导入清单.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("WD练习题 导入清单\n")
        f.write("="*80 + "\n\n")
        f.write(f"统计:\n")
        f.write(f"  成功: {total_stats['success']}\n")
        f.write(f"  失败: {total_stats['failed']}\n")
        f.write(f"  跳过: {total_stats['skipped']}\n")
        f.write(f"\n{'='*80}\n\n")

        current_subject = None
        for item in checklist:
            if item['subject'] != current_subject:
                current_subject = item['subject']
                f.write(f"\n{'='*40}\n")
                f.write(f"【{current_subject}】\n")
                f.write(f"{'='*40}\n")

            if item['status'] == 'success':
                f.write(f"  ✓ 第{item.get('number', '?')}题 [{item.get('chapter', '?')}] -> {item.get('kp_id', '?')}\n")
                f.write(f"    {item.get('question_preview', '')}...\n")
            elif item['status'] == 'ready':
                f.write(f"  ○ 第{item.get('number', '?')}题 [{item.get('chapter', '?')}] -> {item.get('kp_id', '?')}\n")
                f.write(f"    {item.get('question_preview', '')}...\n")
            elif item['status'] == 'failed':
                f.write(f"  ✗ 第{item.get('number', '?')}题: {item.get('reason', '未知错误')}\n")
                f.write(f"    {item.get('question_preview', '')}...\n")
            elif item['status'] == 'skipped':
                f.write(f"  ⊘ {item.get('reason', '')}\n")

    print(f"\n{'='*60}")
    print(f"导入完成!")
    print(f"  成功: {total_stats['success']}")
    print(f"  失败: {total_stats['failed']}")
    print(f"  跳过: {total_stats['skipped']}")
    print(f"\n清单已保存到:")
    print(f"  JSON: {checklist_path}")
    print(f"  TXT:  {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
