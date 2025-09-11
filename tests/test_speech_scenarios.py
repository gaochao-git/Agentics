#!/usr/bin/env python3
"""
测试发言稿智能体的场景识别能力
"""

import requests
import json

BASE_URL = "http://localhost:8000"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

def test_speech_scenarios():
    """测试发言稿智能体的各种场景"""
    test_cases = [
        {
            "scenario": "动员大会",
            "message": "请帮我写一份销售冲刺动员大会的讲话稿，激励团队完成年度目标",
            "expected_type": "动员大会"
        },
        {
            "scenario": "党会发言",
            "message": "需要一份在党支部民主生活会上的发言稿，主题是加强党性修养",
            "expected_type": "党会"
        },
        {
            "scenario": "新年致辞",
            "message": "写一份新年致辞，面向全体员工，回顾过去一年的成就和展望新年",
            "expected_type": "新年致辞"
        },
        {
            "scenario": "就职演说",
            "message": "我刚被任命为部门经理，需要一份就职演说稿",
            "expected_type": "就职"
        },
        {
            "scenario": "表彰大会",
            "message": "在年度先进表彰大会上的讲话稿，表彰优秀员工",
            "expected_type": "表彰"
        }
    ]
    
    print("测试发言稿智能体场景识别")
    print("=" * 40)
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}] 测试场景: {test_case['scenario']}")
        print(f"输入: {test_case['message'][:50]}...")
        
        url = f"{BASE_URL}/api/agents/chat/"
        data = {
            "message": test_case["message"],
            "agent_type": "speech_writer"
        }
        
        try:
            response = requests.post(url, json=data, headers=HEADERS, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                metadata = result.get('metadata', {})
                speech_type = metadata.get('speech_type', '未识别')
                
                print(f"✓ 成功生成")
                print(f"识别场景: {speech_type}")
                print(f"预估时长: {metadata.get('estimated_duration', 'N/A')} 分钟")
                print(f"响应长度: {len(result.get('response', ''))} 字符")
                
                # 检查是否正确识别场景关键词
                if any(keyword in speech_type for keyword in test_case['expected_type'].split()):
                    print("✓ 场景识别正确")
                    success_count += 1
                else:
                    print(f"⚠ 场景识别可能不准确 (期望包含: {test_case['expected_type']})")
                    success_count += 0.5  # 部分成功
                    
            else:
                print(f"✗ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"✗ 异常: {e}")
    
    print(f"\n总结: {success_count}/{len(test_cases)} 场景测试成功")
    return success_count >= len(test_cases) * 0.8  # 80%成功率算通过

if __name__ == "__main__":
    test_speech_scenarios()