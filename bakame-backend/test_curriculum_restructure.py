import asyncio
import os
from app.services.curriculum_service import curriculum_service

async def test_new_curriculum_structure():
    print("=== Testing New Curriculum Structure ===")
    
    expected_modules = ["grammar", "composition", "math", "debate", "comprehension"]
    print(f"Expected modules: {expected_modules}")
    print(f"Loaded modules: {curriculum_service.modules}")
    assert curriculum_service.modules == expected_modules, "Module list mismatch"
    
    for module in expected_modules:
        stages = curriculum_service.curriculum_data.get(module, {})
        print(f"{module}: {len(stages)} stages loaded")
        assert len(stages) == 6, f"Expected 6 stages for {module}, got {len(stages)}"
    
    grammar_tests = [
        ("I go to school yesterday", "grammar", "apply"),
        ("He are my friend", "grammar", "remember"),
        ("What is the past tense of 'go'?", "grammar", "understand")
    ]
    
    print("\n=== Testing Grammar Module Assessment ===")
    for user_input, module, stage in grammar_tests:
        assessment = await curriculum_service.assess_student_response(user_input, module, stage)
        print(f"Input: '{user_input}' | Module: {module} | Stage: {stage}")
        print(f"Score: {assessment['overall_score']:.2f} | Pass: {assessment['is_pass']}")
        print(f"Feedback: {assessment['feedback']}\n")
    
    composition_tests = [
        ("Once upon a time there was a brave girl", "composition", "create"),
        ("The story has a beginning and end", "composition", "understand"),
        ("I want to write about my village", "composition", "apply")
    ]
    
    print("=== Testing Composition Module Assessment ===")
    for user_input, module, stage in composition_tests:
        assessment = await curriculum_service.assess_student_response(user_input, module, stage)
        print(f"Input: '{user_input}' | Module: {module} | Stage: {stage}")
        print(f"Score: {assessment['overall_score']:.2f} | Pass: {assessment['is_pass']}")
        print(f"Feedback: {assessment['feedback']}\n")
    
    print("=== Testing File Structure ===")
    for module in expected_modules:
        for stage in curriculum_service.bloom_stages:
            file_path = f"/home/ubuntu/repos/mvp/bakame-backend/docs/curriculum/{module}/{stage}.md"
            exists = os.path.exists(file_path)
            print(f"{module}/{stage}.md: {'✓' if exists else '✗'}")
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    asyncio.run(test_new_curriculum_structure())
