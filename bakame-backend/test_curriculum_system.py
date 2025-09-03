import asyncio
from app.services.curriculum_service import curriculum_service
from app.services.language_scaffolding_service import language_scaffolding_service

async def test_curriculum_system():
    print("=== Testing Curriculum Service ===")
    
    print(f"Loaded {len(curriculum_service.curriculum_data)} modules")
    for module in curriculum_service.modules:
        stages = curriculum_service.curriculum_data.get(module, {})
        print(f"{module}: {len(stages)} stages loaded")
    
    test_responses = [
        ("My name is John", "english", "remember"),
        ("I go to school yesterday", "english", "apply"),
        ("The story teaches us about helping others", "comprehension", "analyze"),
        ("5 + 3 = 8", "math", "remember")
    ]
    
    for user_input, module, stage in test_responses:
        assessment = await curriculum_service.assess_student_response(user_input, module, stage)
        print(f"Input: '{user_input}' | Module: {module} | Stage: {stage}")
        print(f"Score: {assessment['overall_score']:.2f} | Pass: {assessment['is_pass']}")
        print(f"Feedback: {assessment['feedback']}\n")
    
    print("=== Testing Language Scaffolding ===")
    
    scaffolding_tests = [
        "I go school yesterday",
        "My mother she is teacher",
        "I have went to market",
        "Can you help me please?"
    ]
    
    for test_input in scaffolding_tests:
        corrected, feedback, needs_correction = await language_scaffolding_service.process_with_scaffolding(test_input, focus_on_meaning=False)
        print(f"Original: '{test_input}'")
        print(f"Corrected: '{corrected}'")
        print(f"Feedback: '{feedback}'")
        print(f"Needs correction: {needs_correction}\n")

if __name__ == "__main__":
    asyncio.run(test_curriculum_system())
