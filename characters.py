# prompt: give and print complete set

def get_complete_set():
    # English Alphabet (Upper and Lower Case)
    alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + list('abcdefghijklmnopqrstuvwxyz')

    # Digits
    digits = list('0123456789')

    # Basic Mathematical Symbols
    math_symbols = list('+-×÷=≠≈<≤>≥±∓∞∑∏√∛∜∫∮∂∇∆πθλμω')

    # Special Characters
    special_chars = list("!@#$%^&*()-_=+[]{}|;:'\",.<>?/~`")

    # Logical & Set Theory Symbols
    logical_symbols = list('∀∃∈∉∋')

    # Currency Symbols
    currency_symbols = ['$', '€', '£']

    # Words
    random_words = [
        'apple', 'banana', 'cherry', 'dog', 'elephant', 'fish', 'grape', 'house', 'ice', 'jungle',
        'kite', 'lemon', 'mountain', 'night', 'orange', 'pizza', 'queen', 'river', 'sun', 'tree',
        'umbrella', 'violin', 'water', 'xylophone', 'yacht', 'zebra'
    ]

    # Generate random short phrases
    phrases = [
        'Hello World', 'Good Morning', 'Data Science', 'Machine Learning',
        'Time Series', 'Artificial Intelligence', 'Neural Networks',
        'Deep Learning', 'Pattern Recognition', 'Handwriting Analysis',
        'Blue Car', 'Green Dog', 'Yellow Tree', 'Purple Glass', 'Black Phone'
    ]
    complete_set = set(alphabet + digits + math_symbols + special_chars + logical_symbols + currency_symbols + random_words + phrases)
    return complete_set
