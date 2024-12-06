from fastapi import APIRouter, Query
import pandas as pd
import csv
import os
import json
from models.trademark_model import TrademarkData
from database import get_collection

router = APIRouter(prefix="/combination", tags=["trademark"])

def read_column_from_csv(column_name='Title Name'):
            column_values = []
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dataFiles', 'final.csv')
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # CSV reader
                csv_reader = csv.DictReader(csvfile)
                
                for row in csv_reader:
                    column_values.append(row[column_name])
            
            return column_values

COLUMN_VALUE = read_column_from_csv()

@router.get("/")
async def get_all_data(name: str = Query(..., description="The name to search for")):
    try:
        
        # def read_column_from_csv(file_path, column_name='Title Name'):
        #     column_values = []
            
        #     with open(file_path, 'r', encoding='utf-8') as csvfile:
        #         # CSV reader
        #         csv_reader = csv.DictReader(csvfile)
                
        #         for row in csv_reader:
        #             column_values.append(row[column_name])
            
        #     return column_values
        
        def load_word_list(words_list):
            return set(words_list)

        def is_word_combination(input_string, word_set):
            words = input_string.split()
            
            def can_split(start, memo=None):
                if memo is None:
                    memo = {}
                
                if start == len(words):
                    return True
                
                if start in memo:
                    return memo[start]
                
                for end in range(start + 1, len(words) + 1):
                    current_phrase = ' '.join(words[start:end])
                    
                    if current_phrase in word_set:
                        if can_split(end, memo):
                            memo[start] = True
                            return True
                
                memo[start] = False
                return False
            
            return can_split(0)

        def test_word_combination_checker():
            # title_names = read_column_from_csv(file_path)
            title_names = COLUMN_VALUE
            word_set = load_word_list(title_names)
            
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
                "HINDUSTAN TECHNOLOGY TODAY",
                name
            ]
            
            print("Word Combination Test Results:")
            for input_str in test_inputs:
                print(f"'{input_str}': {is_word_combination(input_str, word_set)}")

            name_validation = is_word_combination(name, word_set)

            return name_validation

        name_validation = test_word_combination_checker()

        if name_validation:
            return {"Message":f"{name} is combination of titles !"}
        else:
            return {"Message":f"{name} is not a combination of titles !"}
    except Exception as e:
        return {"error": str(e.with_traceback())}, 500
    

@router.get("/disallowedPrefix")
async def get_all_data(name: str = Query(..., description="The name to search for")):
    try:

        def check_string(input_str):
            restricted_words = ["POLICE", "CRIME", "CORRUPTION", "CBI", "CID", "ARMY"]
            words = input_str.split()
            
            for word in words:
                if word in restricted_words:
                    return False
            
            return True

        allowed = check_string(name)

        if allowed:
            return {"Message":f"{name} is  allowed !"}
        else:
            return {"Message":f"{name} is not allowed !"}

    except Exception as e:
        return {"error": str(e.with_traceback())}, 500
    






@router.get("/space_nospace")
async def get_all_data(name: str = Query(..., description="The name to search for")):
    try:
        def remove_spaces_variants(s):
            # Generate all possible versions of the string with spaces removed at different positions
            variants = set()
            for i in range(len(s) + 1):
                # Create a variant with spaces removed up to index `i`
                variant = s[:i] + s[i:].replace(" ", "")
                variants.add(variant)
            return variants

        def is_not_in_list(input_string, string_list):
            # Get all variants of the input string (spaces removed at any position)
            input_variants = remove_spaces_variants(input_string.replace(" ", "")) # First remove all spaces from input string
            
            # For each string in the list, generate the variants and check if there's a match
            for string in string_list:
                list_variants = remove_spaces_variants(string.replace(" ", ""))
                if any(variant in list_variants for variant in input_variants):
                    return False
            return True

        allowed = is_not_in_list(name,string_list=COLUMN_VALUE)

        if allowed:
            return {"Message":f"{name} is  allowed !"}
        else:
            return {"Message":f"{name} is not allowed !"}

    except Exception as e:
        return {"error": str(e.with_traceback())}, 500