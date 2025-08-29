import asyncio
import sys
import os
sys.path.append('/home/ubuntu/repos/mvp/bakame-backend')

from app.services.evaluation_engine import evaluation_engine

async def test_evaluation_engine():
    print("=== Testing Advanced Multi-Stage Evaluation Engine ===")
    
    print("\n1. Testing YAML Schema Loading:")
    for module in evaluation_engine.modules:
        for stage in evaluation_engine.bloom_stages:
            schema = evaluation_engine.evaluation_schemas.get(module, {}).get(stage, {})
            if schema and 'ivr_prompt' in schema:
                print(f"✓ {module}/{stage}.yaml loaded successfully")
            else:
                print(f"✗ {module}/{stage}.yaml missing or invalid")
    
    print("\n2. Testing IVR Prompt Generation:")
    user_context = {"user_name": "Amahoro", "phone_number": "+250123456789"}
    
    test_cases = [
        ("grammar", "remember"),
        ("grammar", "apply"),
        ("math", "apply"),
        ("composition", "create"),
        ("debate", "evaluate")
    ]
    
    for module, stage in test_cases:
        prompt = evaluation_engine.get_ivr_prompt(module, stage, user_context)
        print(f"✓ {module}/{stage}: {prompt[:100]}...")
    
    print("\n3. Testing Multi-Factor Evaluation:")
    
    evaluation_tests = [
        {
            "input": "Yesterday I went to school and played with my friends",
            "module": "grammar",
            "stage": "apply",
            "expected_pass": True
        },
        {
            "input": "I go school yesterday and play friends",
            "module": "grammar", 
            "stage": "apply",
            "expected_pass": False
        },
        {
            "input": "3 times 450 is 1350, then 2000 minus 1350 equals 650 francs",
            "module": "math",
            "stage": "apply", 
            "expected_pass": True
        },
        {
            "input": "I think uniforms are good because equality but bad because no creativity. I support uniforms.",
            "module": "debate",
            "stage": "evaluate",
            "expected_pass": True
        },
        {
            "input": "Once there was a brave woman who helped her village during floods. She shared food and shelter.",
            "module": "composition",
            "stage": "create",
            "expected_pass": True
        }
    ]
    
    for test in evaluation_tests:
        result = await evaluation_engine.evaluate_response(
            test["input"], test["module"], test["stage"], user_context
        )
        
        print(f"\nInput: '{test['input'][:50]}...'")
        print(f"Module: {test['module']}, Stage: {test['stage']}")
        print(f"Score: {result['overall_score']:.2f}")
        print(f"Pass: {result['is_pass']} (Expected: {test['expected_pass']})")
        print(f"Emotional State: {result['emotional_state']}")
        print(f"Feedback: {result['feedback']}")
        print(f"Component Scores: K={result['keyword_score']:.2f}, S={result['structure_score']:.2f}, L={result['llm_score']:.2f}")
    
    print("\n4. Testing Emotional State Detection:")
    
    emotional_tests = [
        ("Um, I think maybe it's correct?", "hesitation"),
        ("I don't understand what you mean", "confusion"),
        ("This is too hard, I can't do it", "frustration"),
        ("Yesterday I went to the market", "neutral")
    ]
    
    for input_text, expected_emotion in emotional_tests:
        emotion = await evaluation_engine._detect_emotional_state(input_text, user_context)
        print(f"'{input_text}' → {emotion} (Expected: {expected_emotion})")
    
    print("\n5. Testing Progression Logic:")
    
    phone_number = "+250123456789"
    module = "grammar"
    
    evaluation_engine.log_evaluation(phone_number, module, "remember", {
        "overall_score": 0.8, "is_pass": True, "feedback": "Good work!",
        "emotional_state": "neutral", "schema_used": "grammar_remember",
        "keyword_score": 0.8, "structure_score": 0.8, "llm_score": 0.8
    }, "test input")
    
    evaluation_engine.log_evaluation(phone_number, module, "remember", {
        "overall_score": 0.7, "is_pass": True, "feedback": "Great!",
        "emotional_state": "neutral", "schema_used": "grammar_remember",
        "keyword_score": 0.7, "structure_score": 0.7, "llm_score": 0.7
    }, "test input")
    
    evaluation_engine.log_evaluation(phone_number, module, "remember", {
        "overall_score": 0.9, "is_pass": True, "feedback": "Excellent!",
        "emotional_state": "neutral", "schema_used": "grammar_remember",
        "keyword_score": 0.9, "structure_score": 0.9, "llm_score": 0.9
    }, "test input")
    
    advancement = evaluation_engine.check_advancement(phone_number, module)
    print(f"Advancement result: {advancement}")
    
    print("\n=== Evaluation Engine Testing Complete ===")

if __name__ == "__main__":
    asyncio.run(test_evaluation_engine())
