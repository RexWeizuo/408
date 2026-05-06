import re
import asyncio
import os
from database import async_session, engine
from models import Base, LionSubject, LionLevel1, LionLevel2, LionLevel3, LionLevel4


def parse_toc_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.strip().split('\n')
    
    l1_items = []
    current_l1 = None
    current_l2 = None
    current_l3 = None

    for raw_line in lines:
        line = raw_line.strip()
        
        # Level 1: ### 第一章 计算机系统概述
        if line.startswith('### '):
            current_l1 = {'name': line[4:].strip(), 'children': []}
            current_l2 = None
            current_l3 = None
            l1_items.append(current_l1)
        
        # Level 2: 1.1 操作系统概述
        elif current_l1 and re.match(r'^\d+\.\d+\s', line):
            current_l2 = {'name': line, 'children': []}
            current_l3 = None
            current_l1['children'].append(current_l2)
        
        # Level 3: - 一、xxx
        elif current_l2 and re.match(r'^- [一二三四五六七八九十]+、', line):
            name = line[2:].strip()
            current_l3 = {'name': name, 'children': []}
            current_l2['children'].append(current_l3)
        
        # Level 3 (supplement): - 【补充】xxx (no children)
        elif current_l2 and line.startswith('- 【补充】'):
            name = line[2:].strip()
            current_l2['children'].append({'name': name, 'children': []})
            current_l3 = None
        
        # Level 4: - （一）xxx
        elif current_l3 and re.match(r'^- [（(][一二三四五六七八九十]+[）)]\s*', line):
            name = line[2:].strip()
            current_l3['children'].append({'name': name})

    return l1_items


async def init_lion_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(LionSubject.__table__.select())
            if result.fetchall():
                print("LION数据已存在，跳过导入")
                return

            toc_files = [
                {'subject': 'operating_system', 'name': '操作系统', 'file': 'os_toc_ocr.txt'},
                {'subject': 'computer_organization', 'name': '计算机组成原理', 'file': 'cs_toc_ocr.txt'}
            ]

            for toc_info in toc_files:
                base_dir = os.path.dirname(os.path.dirname(__file__))
                filepath = os.path.join(base_dir, toc_info['file'])
                if not os.path.exists(filepath):
                    print(f"文件不存在: {filepath}")
                    continue

                parsed = parse_toc_file(filepath)

                subject = LionSubject(id=toc_info['subject'], name=toc_info['name'])
                session.add(subject)

                for l1_idx, l1_data in enumerate(parsed):
                    level1 = LionLevel1(
                        id=f"{toc_info['subject']}_l1_{l1_idx+1}",
                        lion_subject_id=toc_info['subject'],
                        name=l1_data['name'],
                        order_index=l1_idx
                    )
                    session.add(level1)

                    for l2_idx, l2_data in enumerate(l1_data.get('children', [])):
                        level2 = LionLevel2(
                            id=f"{toc_info['subject']}_l2_{l1_idx+1}_{l2_idx+1}",
                            level1_id=level1.id,
                            name=l2_data['name'],
                            order_index=l2_idx
                        )
                        session.add(level2)

                        for l3_idx, l3_data in enumerate(l2_data.get('children', [])):
                            level3 = LionLevel3(
                                id=f"{toc_info['subject']}_l3_{l1_idx+1}_{l2_idx+1}_{l3_idx+1}",
                                level2_id=level2.id,
                                name=l3_data['name'],
                                order_index=l3_idx
                            )
                            session.add(level3)

                            for l4_idx, l4_data in enumerate(l3_data.get('children', [])):
                                level4 = LionLevel4(
                                    id=f"{toc_info['subject']}_l4_{l1_idx+1}_{l2_idx+1}_{l3_idx+1}_{l4_idx+1}",
                                    level3_id=level3.id,
                                    name=l4_data['name'],
                                    content="",
                                    order_index=l4_idx
                                )
                                session.add(level4)

            await session.commit()
            print("LION数据导入成功")


if __name__ == "__main__":
    asyncio.run(init_lion_db())
