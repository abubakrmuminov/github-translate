# quiz_data.py - Comprehensive word database for quiz

QUIZ_DATA = {
    "easy": {
        "greetings": [
            "Hello", "Goodbye", "Good morning", "Good night", "Welcome",
            "See you", "How are you?", "Nice to meet you", "Thank you", "Please"
        ],
        "basic_words": [
            "Yes", "No", "Maybe", "Today", "Tomorrow", "Yesterday",
            "Now", "Here", "There", "Where", "When", "Why", "How"
        ],
        "numbers": [
            "One", "Two", "Three", "Four", "Five", "Six", "Seven",
            "Eight", "Nine", "Ten", "Hundred", "Thousand"
        ],
        "colors": [
            "Red", "Blue", "Green", "Yellow", "Black", "White",
            "Orange", "Purple", "Pink", "Brown", "Gray"
        ],
        "family": [
            "Mother", "Father", "Sister", "Brother", "Child", "Baby",
            "Grandmother", "Grandfather", "Aunt", "Uncle", "Cousin"
        ],
        "animals": [
            "Cat", "Dog", "Bird", "Fish", "Horse", "Cow", "Pig",
            "Chicken", "Duck", "Mouse", "Rabbit", "Sheep"
        ],
        "food": [
            "Water", "Bread", "Milk", "Egg", "Cheese", "Rice",
            "Apple", "Banana", "Orange", "Meat", "Fish", "Chicken"
        ],
        "body": [
            "Head", "Hand", "Foot", "Eye", "Ear", "Nose", "Mouth",
            "Hair", "Arm", "Leg", "Face", "Body"
        ],
        "nature": [
            "Sun", "Moon", "Star", "Sky", "Cloud", "Rain", "Snow",
            "Tree", "Flower", "Mountain", "River", "Sea"
        ]
    },
    
    "medium": {
        "emotions": [
            "Happy", "Sad", "Angry", "Excited", "Tired", "Hungry",
            "Thirsty", "Scared", "Worried", "Surprised", "Bored", "Proud"
        ],
        "actions": [
            "Eat", "Drink", "Sleep", "Walk", "Run", "Jump", "Sit",
            "Stand", "Read", "Write", "Speak", "Listen", "Think"
        ],
        "places": [
            "Home", "School", "Hospital", "Restaurant", "Hotel", "Airport",
            "Station", "Bank", "Post office", "Library", "Museum", "Park"
        ],
        "time": [
            "Morning", "Afternoon", "Evening", "Night", "Week", "Month",
            "Year", "Hour", "Minute", "Second", "Weekend", "Holiday"
        ],
        "weather": [
            "Hot", "Cold", "Warm", "Cool", "Sunny", "Cloudy", "Rainy",
            "Snowy", "Windy", "Foggy", "Storm", "Thunder"
        ],
        "clothes": [
            "Shirt", "Pants", "Dress", "Skirt", "Shoes", "Socks",
            "Hat", "Coat", "Jacket", "Sweater", "Gloves", "Scarf"
        ],
        "professions": [
            "Teacher", "Doctor", "Engineer", "Artist", "Driver", "Cook",
            "Nurse", "Police officer", "Firefighter", "Pilot", "Farmer"
        ],
        "transport": [
            "Car", "Bus", "Train", "Plane", "Bicycle", "Motorcycle",
            "Boat", "Ship", "Taxi", "Subway", "Truck"
        ],
        "adjectives": [
            "Big", "Small", "Tall", "Short", "Long", "Fast", "Slow",
            "Beautiful", "Ugly", "Good", "Bad", "New", "Old", "Young"
        ],
        "phrases": [
            "I love you", "I'm sorry", "Excuse me", "You're welcome",
            "I don't know", "I understand", "Help me", "See you later"
        ]
    },
    
    "hard": {
        "advanced_verbs": [
            "Accomplish", "Achieve", "Analyze", "Appreciate", "Argue",
            "Assume", "Attempt", "Avoid", "Believe", "Celebrate",
            "Compare", "Complain", "Conclude", "Confirm", "Consider"
        ],
        "abstract_nouns": [
            "Freedom", "Justice", "Knowledge", "Wisdom", "Truth",
            "Beauty", "Courage", "Patience", "Honesty", "Creativity",
            "Democracy", "Philosophy", "Psychology", "Education"
        ],
        "complex_adjectives": [
            "Ambitious", "Anxious", "Brilliant", "Careful", "Curious",
            "Determined", "Efficient", "Enthusiastic", "Generous",
            "Imaginative", "Independent", "Responsible", "Sensitive"
        ],
        "idioms": [
            "Break the ice", "Once in a blue moon", "Piece of cake",
            "Hit the nail on the head", "Costs an arm and a leg",
            "Under the weather", "Blessing in disguise", "Call it a day"
        ],
        "business": [
            "Agreement", "Investment", "Profit", "Budget", "Strategy",
            "Management", "Marketing", "Negotiation", "Partnership",
            "Competition", "Innovation", "Development", "Analysis"
        ],
        "technology": [
            "Computer", "Internet", "Software", "Hardware", "Database",
            "Algorithm", "Programming", "Security", "Network", "Server",
            "Application", "Interface", "Technology", "Digital"
        ],
        "science": [
            "Experiment", "Research", "Theory", "Hypothesis", "Evidence",
            "Discovery", "Laboratory", "Chemistry", "Physics", "Biology",
            "Mathematics", "Analysis", "Observation", "Conclusion"
        ],
        "complex_phrases": [
            "It's raining cats and dogs", "The early bird catches the worm",
            "Actions speak louder than words", "Don't put all your eggs in one basket",
            "Every cloud has a silver lining", "Rome wasn't built in a day",
            "When in Rome, do as the Romans do", "Better late than never"
        ],
        "academic": [
            "University", "Scholarship", "Degree", "Research", "Thesis",
            "Professor", "Lecture", "Assignment", "Examination", "Graduate",
            "Curriculum", "Semester", "Academic", "Knowledge"
        ]
    }
}

# Points system
DIFFICULTY_POINTS = {
    "easy": 10,
    "medium": 20,
    "hard": 30
}

# Streak bonuses
STREAK_BONUS = {
    3: 5,   # 3 in a row: +5 bonus
    5: 15,  # 5 in a row: +15 bonus
    10: 50, # 10 in a row: +50 bonus
    20: 100 # 20 in a row: +100 bonus
}

# Level requirements (XP needed for each level)
LEVEL_REQUIREMENTS = {
    1: 0,
    2: 100,
    3: 250,
    4: 500,
    5: 1000,
    6: 2000,
    7: 3500,
    8: 5500,
    9: 8000,
    10: 11000,
    11: 15000,
    12: 20000,
    13: 26000,
    14: 33000,
    15: 41000,
    16: 50000,
    17: 60000,
    18: 71000,
    19: 83000,
    20: 100000
}

def get_random_word(difficulty: str) -> tuple:
    """Get a random word from the specified difficulty level"""
    import random
    
    if difficulty not in QUIZ_DATA:
        difficulty = "medium"
    
    # Choose random category
    category = random.choice(list(QUIZ_DATA[difficulty].keys()))
    word = random.choice(QUIZ_DATA[difficulty][category])
    
    return word, category

def get_all_words_except(difficulty: str, exclude_word: str, count: int = 3) -> list:
    """Get random words from same difficulty, excluding specific word"""
    import random
    
    all_words = []
    for category in QUIZ_DATA[difficulty].values():
        all_words.extend(category)
    
    # Remove the word to exclude
    available_words = [w for w in all_words if w != exclude_word]
    
    return random.sample(available_words, min(count, len(available_words)))

def calculate_level(xp: int) -> int:
    """Calculate player level based on XP"""
    level = 1
    for lvl, required_xp in sorted(LEVEL_REQUIREMENTS.items()):
        if xp >= required_xp:
            level = lvl
        else:
            break
    return level

def get_xp_for_next_level(current_xp: int) -> tuple:
    """Returns (current_level, next_level_xp, xp_needed)"""
    current_level = calculate_level(current_xp)
    next_level = current_level + 1
    
    if next_level in LEVEL_REQUIREMENTS:
        next_level_xp = LEVEL_REQUIREMENTS[next_level]
        xp_needed = next_level_xp - current_xp
        return current_level, next_level_xp, xp_needed
    else:
        return current_level, None, None  # Max level reached