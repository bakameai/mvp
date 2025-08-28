import asyncio
from app.services.name_extraction_service import name_extraction_service

async def test_name_extraction():
    print("=== Testing Name Extraction ===")
    
    test_cases = [
        "My name is Kevin",
        "I am Sarah", 
        "John",
        "It's Michael",
        "Call me David",
        "unclear mumbling",
        "I'm called Emmanuel",
        "You can call me Grace"
    ]
    
    for test_input in test_cases:
        name, confidence = name_extraction_service.extract_name(test_input)
        print(f"Input: '{test_input}' -> Name: {name}, Confidence: {confidence}")
    
    print("\n=== Testing Intro Generation ===")
    intro = await name_extraction_service.generate_intro_message()
    print(f"Generated intro: {intro}")
    
    print("\n=== Testing Confirmation Detection ===")
    confirmations = ["yes that's right", "no my name is bob", "correct", "nope", "yeah", "mhmm"]
    for conf in confirmations:
        is_conf = name_extraction_service.is_confirmation(conf)
        print(f"'{conf}' is confirmation: {is_conf}")
    
    print("\n=== Testing Spelling Extraction ===")
    spelling_tests = ["k e v i n", "alpha bravo charlie", "dee ay vee eye dee"]
    for spell_input in spelling_tests:
        spelled = name_extraction_service.extract_spelling(spell_input)
        print(f"Spelling '{spell_input}' -> '{spelled}'")

if __name__ == "__main__":
    asyncio.run(test_name_extraction())
