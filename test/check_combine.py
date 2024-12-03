import csv

def read_column_from_csv(file_path, column_name='Title Name'):
    """
    Read a specific column from a CSV file.
    
    :param file_path: Path to the CSV file
    :param column_name: Name of the column to extract
    :return: List of values from the specified column
    """
    column_values = []
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        # CSV reader
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            column_values.append(row[column_name])
    
    return column_values

def load_word_list(words_list):
    """
    Convert the list of words into a set for efficient lookup.
    
    :param words_list: List of words or phrases to be used as a dictionary
    :return: Set of words/phrases for fast checking
    """
    return set(words_list)

def is_word_combination(input_string, word_set):
    """
    Check if the input string is a combination of words from the word set.
    
    :param input_string: String to check
    :param word_set: Set of valid words/phrases
    :return: Boolean indicating if the string is a valid word combination
    """
    # Split the input string into words
    words = input_string.split()
    
    # Try all possible combinations of splitting the input
    def can_split(start, memo=None):
        # Memoization to optimize recursive calls
        if memo is None:
            memo = {}
        
        # Base case: reached the end of the string
        if start == len(words):
            return True
        
        # Check memoized results
        if start in memo:
            return memo[start]
        
        # Try all possible splits from this starting point
        for end in range(start + 1, len(words) + 1):
            # Get the current substring
            current_phrase = ' '.join(words[start:end])
            
            # Check if current phrase is in word set
            if current_phrase in word_set:
                # Recursively check the rest of the string
                if can_split(end, memo):
                    memo[start] = True
                    return True
        
        # No valid split found
        memo[start] = False
        return False
    
    # Attempt to split the entire input
    return can_split(0)

def test_word_combination_checker(file_path='test/final.csv'):
    """
    Test the word combination checker using titles from a CSV file.
    
    :param file_path: Path to the CSV file containing titles
    """
    # Read titles from CSV
    title_names = read_column_from_csv(file_path)
    
    # Create an efficient word set
    word_set = load_word_list(title_names)
    
    # Test cases
    test_inputs = [
        "JAN JAGRAN YOGIC SCIENCES",
        "DAINIK JAGRAN",
        "DAINIK JAGRAN JAN JAGRAN YOGIC SCIENCES",
        "JAN JAGRAN YOGIC SCIENCES DAINIK JAGRAN",
        "DAINIK YOGIC SCIENCES",
        "DAINIK JAN JAGRAN YOGIC SCIENCES",
        "YOGIC SCIENCES",
        "HINDUSTAN TIMES",
        "TECHNOLOGY TODAY",
        "TECHNOLOGY TODAY HINDUSTAN TIMES",
        "HINDUSTAN TIMES TECHNOLOGY TODAY",
        "HINDUSTAN TECHNOLOGY TODAY"
    ]
    
    # Run tests
    print("Word Combination Test Results:")
    for input_str in test_inputs:
        print(f"'{input_str}': {is_word_combination(input_str, word_set)}")

# Run the tests when the script is executed
if __name__ == "__main__":
    test_word_combination_checker()