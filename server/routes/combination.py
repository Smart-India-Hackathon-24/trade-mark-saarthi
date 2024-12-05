from fastapi import APIRouter, Query
import pandas as pd
import csv

import json
from models.trademark_model import TrademarkData
from database import get_collection

router = APIRouter(prefix="/combination", tags=["trademark"])

def read_column_from_csv(file_path='D:/Projects/Hackathons/SIH\'24/trade-mark-saarthi/dataFiles/final.csv', column_name='Title Name'):
            column_values = []
            
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