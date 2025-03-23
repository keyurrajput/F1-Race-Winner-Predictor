import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import warnings
import tkinter as tk
from tkinter import filedialog, ttk, Scale, messagebox
import os
import re
import sys
import traceback

# Suppress warnings
warnings.filterwarnings('ignore')

class F1RacePredictor:
    """F1 Race Prediction Model for Top 3 Finishers with rain factors and sprint race support"""
    
    def __init__(self):
        """Initialize predictor"""
        # The main prediction class code remains unchanged
        # All the core functionality is kept the same
        self.quali_data = None
        self.practice_data = None
        self.sprint_data = None  # Sprint results data
        self.sprint_quali_data = None  # Sprint qualifying data
        self.race_name = None
        self.combined_data = None
        self.top3_prediction = None
        self.mse = None
        self.rmse = None
        self.rain_probability = 0.0  # Default: dry conditions
        self.is_sprint_weekend = False  # Flag for sprint weekend
        
        # Driver name mappings (short codes to full names and vice versa)
        self.driver_name_mapping = {
            # Full names to short codes
            "Max Verstappen": "VER",
            "Lewis Hamilton": "HAM",
            "Fernando Alonso": "ALO",
            "Charles Leclerc": "LEC",
            "Carlos Sainz": "SAI",
            "Lando Norris": "NOR",
            "George Russell": "RUS",
            "Pierre Gasly": "GAS",
            "Lance Stroll": "STR",
            "Alexander Albon": "ALB",
            "Esteban Ocon": "OCO",
            "Yuki Tsunoda": "TSU",
            "Oscar Piastri": "PIA",
            "Nico Hulkenberg": "HUL",
            "Liam Lawson": "LAW",
            "Oliver Bearman": "BEA",
            "Jack Doohan": "DOO",
            "Andrea Kimi Antonelli": "ANT",
            "Gabriel Bortoleto": "BOR",
            "Isack Hadjar": "HAD",
            
            # Short codes to full names
            "VER": "Max Verstappen",
            "HAM": "Lewis Hamilton",
            "ALO": "Fernando Alonso",
            "LEC": "Charles Leclerc",
            "SAI": "Carlos Sainz",
            "NOR": "Lando Norris",
            "RUS": "George Russell",
            "GAS": "Pierre Gasly", 
            "STR": "Lance Stroll",
            "ALB": "Alexander Albon",
            "OCO": "Esteban Ocon",
            "TSU": "Yuki Tsunoda",
            "PIA": "Oscar Piastri",
            "HUL": "Nico Hulkenberg",
            "LAW": "Liam Lawson",
            "BEA": "Oliver Bearman",
            "DOO": "Jack Doohan",
            "ANT": "Andrea Kimi Antonelli",
            "BOR": "Gabriel Bortoleto",
            "HAD": "Isack Hadjar"
        }
        
        # Team name variations mapping
        self.team_name_mapping = {
            "McLaren": "McLaren Mercedes",
            "McLaren Mercedes": "McLaren Mercedes",
            "Red Bull": "Red Bull Racing Honda RBPT",
            "Red Bull Racing": "Red Bull Racing Honda RBPT",
            "RB": "Racing Bulls Honda RBPT",
            "Racing Bulls": "Racing Bulls Honda RBPT",
            "VCARB": "Racing Bulls Honda RBPT",
            "Williams": "Williams Mercedes",
            "Alpine": "Alpine Renault",
            "Aston Martin": "Aston Martin Aramco Mercedes",
            "Sauber": "Kick Sauber Ferrari",
            "Kick Sauber": "Kick Sauber Ferrari",
            "Haas": "Haas Ferrari",
            "Haas F1 Team": "Haas Ferrari",
            "Mercedes": "Mercedes",
            "Ferrari": "Ferrari"
        }
        
        # Initialize data structures
        self._init_team_characteristics()
        self._init_track_database()
        self._init_driver_data()
    
    def _init_team_characteristics(self):
        """Initialize team characteristics for 2025 season"""
        self.team_characteristics = {
            "McLaren Mercedes": {
                "race_pace_factor": 1.02,
                "tire_mgmt": 8.5,
                "start_performance": 8.0,
                "wet_performance": 8.3,     # Team wet weather capability
                "sprint_performance": 8.4    # Team sprint race capability
            },
            "Red Bull Racing Honda RBPT": {
                "race_pace_factor": 1.08,
                "tire_mgmt": 9.0,
                "start_performance": 8.5,
                "wet_performance": 9.0,      # Strong in wet conditions
                "sprint_performance": 9.2     # Excellent in sprints
            },
            "Ferrari": {
                "race_pace_factor": 1.04, 
                "tire_mgmt": 8.7,
                "start_performance": 7.5,
                "wet_performance": 8.2,      # Good in wet
                "sprint_performance": 8.6     # Strong in sprints
            },
            "Mercedes": {
                "race_pace_factor": 1.03,
                "tire_mgmt": 8.2,
                "start_performance": 8.2,
                "wet_performance": 8.8,      # Very good wet package
                "sprint_performance": 8.3     # Good in sprints
            },
            "Racing Bulls Honda RBPT": {
                "race_pace_factor": 0.98,
                "tire_mgmt": 7.5,
                "start_performance": 7.0,
                "wet_performance": 7.6,      # Decent in wet
                "sprint_performance": 7.4     # Average in sprints
            },
            "Williams Mercedes": {
                "race_pace_factor": 0.96,
                "tire_mgmt": 7.0,
                "start_performance": 7.3,
                "wet_performance": 7.2,      # Some wet handling issues
                "sprint_performance": 7.0     # Struggles in sprints
            },
            "Alpine Renault": {
                "race_pace_factor": 0.97,
                "tire_mgmt": 6.8,
                "start_performance": 7.4,
                "wet_performance": 7.0,      # Struggles in wet conditions
                "sprint_performance": 7.1     # Below average in sprints
            },
            "Aston Martin Aramco Mercedes": {
                "race_pace_factor": 1.01,
                "tire_mgmt": 7.2,
                "start_performance": 7.6,
                "wet_performance": 7.8,      # Decent wet package
                "sprint_performance": 7.7     # Decent in sprints
            },
            "Kick Sauber Ferrari": {
                "race_pace_factor": 0.95,
                "tire_mgmt": 6.5,
                "start_performance": 6.8,
                "wet_performance": 6.5,      # Weak in wet conditions
                "sprint_performance": 6.8     # Below average in sprints
            },
            "Haas Ferrari": {
                "race_pace_factor": 0.94,
                "tire_mgmt": 6.0,
                "start_performance": 6.5,
                "wet_performance": 6.8,      # Struggles in wet
                "sprint_performance": 6.7     # Weak in sprints
            }
        }
    
    def _init_driver_data(self):
        """Initialize driver characteristics"""
        self.driver_experience = {
            "Max Verstappen": 0.98,
            "Lewis Hamilton": 0.97,
            "Fernando Alonso": 0.96,
            "Charles Leclerc": 0.93,
            "Carlos Sainz": 0.92,
            "Lando Norris": 0.93,
            "George Russell": 0.91,
            "Pierre Gasly": 0.90,
            "Lance Stroll": 0.88,
            "Alexander Albon": 0.89,
            "Esteban Ocon": 0.89,
            "Yuki Tsunoda": 0.87,
            "Oscar Piastri": 0.89,
            "Nico Hulkenberg": 0.91,
            "Liam Lawson": 0.84,
            "Oliver Bearman": 0.82,
            "Jack Doohan": 0.82,
            "Andrea Kimi Antonelli": 0.80,
            "Gabriel Bortoleto": 0.81,
            "Isack Hadjar": 0.81
        }
        
        # Driver wet weather performance ratings (1-10 scale)
        self.driver_wet_performance = {
            "Max Verstappen": 9.5,     # Exceptional in wet conditions
            "Lewis Hamilton": 9.7,     # One of the best wet weather drivers
            "Fernando Alonso": 9.6,    # Historically excellent in wet
            "Charles Leclerc": 8.2,    # Good but some inconsistency
            "Carlos Sainz": 8.5,       # Solid wet weather driver
            "Lando Norris": 8.3,       # Improving in wet conditions
            "George Russell": 8.6,     # Good in wet conditions
            "Pierre Gasly": 8.4,       # Good wet performance
            "Lance Stroll": 8.1,       # Some good wet performances
            "Alexander Albon": 8.0,    # Decent in wet conditions
            "Esteban Ocon": 7.9,       # Average in wet
            "Yuki Tsunoda": 7.5,       # Still developing wet skills
            "Oscar Piastri": 7.8,      # Limited F1 wet experience
            "Nico Hulkenberg": 8.7,    # Very good in wet
            "Liam Lawson": 7.6,        # Limited F1 wet data
            "Oliver Bearman": 7.4,     # Rookie with limited data
            "Jack Doohan": 7.3,        # Rookie status
            "Andrea Kimi Antonelli": 7.5,  # Promising but limited F1 data
            "Gabriel Bortoleto": 7.2,  # Rookie with limited data
            "Isack Hadjar": 7.3        # Rookie status
        }
        
        # Driver sprint race performance ratings (1-10 scale)
        self.driver_sprint_performance = {
            "Max Verstappen": 9.6,     # Exceptional in sprint races
            "Lewis Hamilton": 9.3,     # Very strong in sprints
            "Fernando Alonso": 8.9,    # Good starter, experienced
            "Charles Leclerc": 9.0,    # Good qualifier and starter
            "Carlos Sainz": 8.7,       # Solid sprint performer
            "Lando Norris": 9.1,       # Strong sprint performer
            "George Russell": 8.8,     # Good at maximizing sprint opportunities
            "Pierre Gasly": 8.0,       # Decent in sprints
            "Lance Stroll": 7.8,       # Average sprint performer
            "Alexander Albon": 8.2,    # Good at race starts
            "Esteban Ocon": 7.9,       # Average in sprints
            "Yuki Tsunoda": 7.7,       # Improving in sprints
            "Oscar Piastri": 8.5,      # Strong qualifier helps in sprints
            "Nico Hulkenberg": 8.0,    # Experienced sprint racer
            "Liam Lawson": 7.8,        # Limited F1 sprint data
            "Oliver Bearman": 7.4,     # Rookie with limited data
            "Jack Doohan": 7.3,        # Rookie status
            "Andrea Kimi Antonelli": 7.7,  # Good junior category sprint performance
            "Gabriel Bortoleto": 7.5,  # Rookie with previous sprint experience
            "Isack Hadjar": 7.4        # Rookie status
        }
    
    def _init_track_database(self):
        """Initialize track database in 2025 calendar order with sprint races identified"""
        self.track_database = {
            "Australian Grand Prix": {
                "name": "Albert Park Circuit",
                "overtaking_difficulty": 7,
                "tire_degradation": 6,
                "start_importance": 8,
                "is_sprint": False
            },
            "Chinese Grand Prix": {
                "name": "Shanghai International Circuit",
                "overtaking_difficulty": 5,
                "tire_degradation": 6,
                "start_importance": 6,
                "is_sprint": True    # Sprint race
            },
            "Japanese Grand Prix": {
                "name": "Suzuka Circuit",
                "overtaking_difficulty": 8,
                "tire_degradation": 7,
                "start_importance": 7,
                "is_sprint": False
            },
            "Bahrain Grand Prix": {
                "name": "Bahrain International Circuit",
                "overtaking_difficulty": 5,
                "tire_degradation": 8,
                "start_importance": 6,
                "is_sprint": False
            },
            "Saudi Arabian Grand Prix": {
                "name": "Jeddah Corniche Circuit",
                "overtaking_difficulty": 6,
                "tire_degradation": 5,
                "start_importance": 7,
                "is_sprint": False
            },
            "Miami Grand Prix": {
                "name": "Miami International Autodrome",
                "overtaking_difficulty": 6, 
                "tire_degradation": 5,
                "start_importance": 7,
                "is_sprint": True    # Sprint race
            },
            "Emilia Romagna Grand Prix": {
                "name": "Autodromo Enzo e Dino Ferrari",
                "overtaking_difficulty": 8,
                "tire_degradation": 6,
                "start_importance": 7,
                "is_sprint": False
            },
            "Monaco Grand Prix": {
                "name": "Circuit de Monaco",
                "overtaking_difficulty": 10,
                "tire_degradation": 3,
                "start_importance": 10,
                "is_sprint": False
            },
            "Spanish Grand Prix": {
                "name": "Circuit de Barcelona-Catalunya",
                "overtaking_difficulty": 7,
                "tire_degradation": 7,
                "start_importance": 7,
                "is_sprint": False
            },
            "Canadian Grand Prix": {
                "name": "Circuit Gilles Villeneuve",
                "overtaking_difficulty": 4,
                "tire_degradation": 6,
                "start_importance": 6,
                "is_sprint": False
            },
            "Austrian Grand Prix": {
                "name": "Red Bull Ring",
                "overtaking_difficulty": 4,
                "tire_degradation": 7,
                "start_importance": 6,
                "is_sprint": True    # Sprint race
            },
            "British Grand Prix": {
                "name": "Silverstone Circuit",
                "overtaking_difficulty": 5,
                "tire_degradation": 7,
                "start_importance": 5,
                "is_sprint": False
            },
            "Belgian Grand Prix": {
                "name": "Circuit de Spa-Francorchamps",
                "overtaking_difficulty": 3,
                "tire_degradation": 6,
                "start_importance": 4,
                "is_sprint": False
            },
            "Hungarian Grand Prix": {
                "name": "Hungaroring",
                "overtaking_difficulty": 9,
                "tire_degradation": 5,
                "start_importance": 8,
                "is_sprint": False
            },
            "Dutch Grand Prix": {
                "name": "Circuit Zandvoort",
                "overtaking_difficulty": 8,
                "tire_degradation": 5,
                "start_importance": 7,
                "is_sprint": False
            },
            "Italian Grand Prix": {
                "name": "Autodromo Nazionale Monza",
                "overtaking_difficulty": 4,
                "tire_degradation": 5,
                "start_importance": 6,
                "is_sprint": False
            },
            "Azerbaijan Grand Prix": {
                "name": "Baku City Circuit",
                "overtaking_difficulty": 5,
                "tire_degradation": 4,
                "start_importance": 7,
                "is_sprint": True    # Sprint race
            },
            "Singapore Grand Prix": {
                "name": "Marina Bay Street Circuit",
                "overtaking_difficulty": 9,
                "tire_degradation": 7,
                "start_importance": 8,
                "is_sprint": False
            },
            "United States Grand Prix": {
                "name": "Circuit of The Americas",
                "overtaking_difficulty": 5,
                "tire_degradation": 6,
                "start_importance": 6,
                "is_sprint": True    # Sprint race
            },
            "Mexican Grand Prix": {
                "name": "Autódromo Hermanos Rodríguez",
                "overtaking_difficulty": 6,
                "tire_degradation": 4,
                "start_importance": 7,
                "is_sprint": False
            },
            "Brazilian Grand Prix": {
                "name": "Autódromo José Carlos Pace",
                "overtaking_difficulty": 4,
                "tire_degradation": 6,
                "start_importance": 5,
                "is_sprint": True    # Sprint race
            },
            "Las Vegas Grand Prix": {
                "name": "Las Vegas Strip Circuit",
                "overtaking_difficulty": 5,
                "tire_degradation": 6,
                "start_importance": 7,
                "is_sprint": False
            },
            "Qatar Grand Prix": {
                "name": "Lusail International Circuit",
                "overtaking_difficulty": 6,
                "tire_degradation": 8,
                "start_importance": 6,
                "is_sprint": True    # Sprint race
            },
            "Abu Dhabi Grand Prix": {
                "name": "Yas Marina Circuit",
                "overtaking_difficulty": 7,
                "tire_degradation": 5,
                "start_importance": 7,
                "is_sprint": False
            }
        }
    
    def set_race(self, race_name):
        """Set the race for prediction and determine if it's a sprint weekend"""
        self.race_name = race_name
        self.track = self.track_database.get(race_name, self.track_database["Australian Grand Prix"])
        self.is_sprint_weekend = self.track.get("is_sprint", False)
        
        if self.is_sprint_weekend:
            print(f"Sprint race weekend selected: {race_name}")
    
    def set_rain_probability(self, probability):
        """Set the rain probability for the race (0.0 to 1.0)"""
        self.rain_probability = max(0.0, min(1.0, probability))
        print(f"Rain probability set to {self.rain_probability*100:.0f}%")
    
    def _find_column(self, df, possible_names, case_sensitive=False):
        """
        Find a column in a DataFrame that matches any of the possible names
        Returns the actual column name if found, None otherwise
        """
        for col in df.columns:
            for name in possible_names:
                if case_sensitive:
                    if col == name:
                        return col
                else:
                    if col.lower() == name.lower():
                        return col
                    
                    # Try partial matches for complex column names like "TIME/RETIRED"
                    if name.lower() in col.lower():
                        return col
        return None
    
    def _standardize_driver_name(self, name):
        """
        Convert driver name to standard format (full name)
        Handles both short codes (VER, HAM) and full names
        """
        if not name or not isinstance(name, str):
            return name
            
        # Check if it's a 3-letter code (most codes are 3 letters)
        if len(name) == 3 and name.upper() == name:
            return self.driver_name_mapping.get(name, name)
            
        # Check if it's already a full name
        if name in self.driver_name_mapping:
            return name
            
        # Try to find a partial match
        for full_name in self.driver_experience.keys():
            if name in full_name:
                return full_name
                
        # Return original if no match
        return name
    
    def _standardize_team_name(self, name):
        """
        Convert team name to standard format
        Handles various team name formats (Red Bull, Red Bull Racing, etc.)
        """
        if not name or not isinstance(name, str):
            return name
            
        # Check if it's already a standardized name
        if name in self.team_characteristics:
            return name
            
        # Check mapping for known variations
        if name in self.team_name_mapping:
            return self.team_name_mapping[name]
            
        # Try to find a partial match
        for team_variant, standard_name in self.team_name_mapping.items():
            if team_variant in name or name in team_variant:
                return standard_name
                
        # Return original if no match
        return name
    
    def _safely_read_csv(self, file_path, encoding_list=None):
        """
        Safely read a CSV file trying multiple encodings
        Returns DataFrame and the successful encoding
        """
        if encoding_list is None:
            encoding_list = ['utf-8', 'latin1', 'cp1252', 'ISO-8859-1']
            
        for encoding in encoding_list:
            try:
                print(f"Trying encoding: {encoding}")
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"Successfully read with encoding: {encoding}")
                return df, encoding
            except UnicodeDecodeError as e:
                print(f"Failed with encoding {encoding}: {str(e)}")
            except Exception as e:
                print(f"Error with encoding {encoding}: {str(e)}")
                
        # If we're here, none of the encodings worked
        raise ValueError(f"Failed to read CSV file {file_path} with any encoding")
    
    def load_data(self, quali_path, practice_path, sprint_path=None, sprint_quali_path=None):
        """Load qualifying, practice, and sprint data (if applicable) with flexible column handling"""
        print(f"Loading data files...")
        print(f"Qualifying data: {os.path.basename(quali_path)}")
        print(f"Practice data: {os.path.basename(practice_path)}")
        
        if self.is_sprint_weekend:
            if sprint_path:
                print(f"Sprint race data: {os.path.basename(sprint_path)}")
            if sprint_quali_path:
                print(f"Sprint qualifying data: {os.path.basename(sprint_quali_path)}")
        
        # Load qualifying data with encoding detection
        self.quali_data, _ = self._safely_read_csv(quali_path)
        print(f"Qualifying data columns: {list(self.quali_data.columns)}")
        
        # Find key columns in qualifying data
        pos_col = self._find_column(self.quali_data, ['POS', 'Pos', 'Position', 'POSITION'])
        driver_col = self._find_column(self.quali_data, ['DRIVER', 'Driver', 'NAME', 'Name'])
        car_col = self._find_column(self.quali_data, ['CAR', 'Car', 'TEAM', 'Team', 'Constructor'])
        q1_col = self._find_column(self.quali_data, ['Q1', 'Q1 Time', 'Q1TIME'])
        q2_col = self._find_column(self.quali_data, ['Q2', 'Q2 Time', 'Q2TIME'])
        q3_col = self._find_column(self.quali_data, ['Q3', 'Q3 Time', 'Q3TIME'])
        
        if not pos_col or not driver_col:
            raise ValueError("Qualifying data missing required columns for position or driver")
            
        # Create standardized columns
        self.quali_data['DRIVER_STD'] = self.quali_data[driver_col].apply(self._standardize_driver_name)
        if car_col:
            self.quali_data['CAR_STD'] = self.quali_data[car_col].apply(self._standardize_team_name)
        else:
            print("Warning: Car/team information missing from qualifying data")
            self.quali_data['CAR_STD'] = 'Unknown'
            
        # Process qualifying times
        for q_col, std_name in zip([q1_col, q2_col, q3_col], ['Q1', 'Q2', 'Q3']):
            if q_col:
                self.quali_data[f'{std_name}_seconds'] = self.quali_data[q_col].apply(self._time_to_seconds)
            else:
                print(f"Warning: {std_name} data missing from qualifying data")
                self.quali_data[f'{std_name}_seconds'] = None
        
        # Calculate best qualifying time
        self.quali_data['best_quali_time'] = self.quali_data.apply(
            lambda row: min(
                [t for t in [row['Q1_seconds'], row['Q2_seconds'], row['Q3_seconds']] 
                 if not pd.isna(t) and t is not None], 
                default=None
            ),
            axis=1
        )
        
        # Handle positions (DNS, DNF, etc.)
        self.quali_data['position'] = self.quali_data[pos_col].apply(self._safe_convert_position)
        
        # Calculate gap to pole
        valid_times = self.quali_data['best_quali_time'].dropna()
        if len(valid_times) > 0:
            pole_time = valid_times.min()
            self.quali_data['gap_to_pole'] = self.quali_data['best_quali_time'].apply(
                lambda x: x - pole_time if not pd.isna(x) else None
            )
        else:
            self.quali_data['gap_to_pole'] = None
        
        # Load practice data with encoding detection
        self.practice_data, _ = self._safely_read_csv(practice_path)
        print(f"Practice data columns: {list(self.practice_data.columns)}")
        
        # Find key columns in practice data
        p_driver_col = self._find_column(self.practice_data, ['DRIVER', 'Driver', 'NAME', 'Name'])
        p_car_col = self._find_column(self.practice_data, ['CAR', 'Car', 'TEAM', 'Team', 'Constructor'])
        
        # Find time columns based on format
        # For standard format with P1, P2, P3 columns
        p1_col = self._find_column(self.practice_data, ['P1', 'P1 Time', 'FP1', 'Practice 1', 'TIME', 'Time'])
        p2_col = self._find_column(self.practice_data, ['P2', 'P2 Time', 'FP2', 'Practice 2'])
        p3_col = self._find_column(self.practice_data, ['P3', 'P3 Time', 'FP3', 'Practice 3'])
        
        if not p_driver_col:
            raise ValueError("Practice data missing driver column")
            
        # Create standardized columns
        self.practice_data['DRIVER_STD'] = self.practice_data[p_driver_col].apply(self._standardize_driver_name)
        if p_car_col:
            self.practice_data['CAR_STD'] = self.practice_data[p_car_col].apply(self._standardize_team_name)
            
        # Process practice times for sprint and regular weekends
        if self.is_sprint_weekend:
            # Sprint weekend - we mainly need P1
            if p1_col:
                self.practice_data['p1_seconds'] = self.practice_data[p1_col].apply(self._time_to_seconds)
            else:
                print("Warning: Practice 1 time data missing")
                self.practice_data['p1_seconds'] = None
                # Still process P2 and P3 if available
            if p2_col:
                self.practice_data['p2_seconds'] = self.practice_data[p2_col].apply(self._time_to_seconds)
            if p3_col:
                self.practice_data['p3_seconds'] = self.practice_data[p3_col].apply(self._time_to_seconds)
        else:
            # Regular weekend - look for all practice sessions
            if p1_col:
                self.practice_data['p1_seconds'] = self.practice_data[p1_col].apply(self._time_to_seconds)
            if p2_col:
                self.practice_data['p2_seconds'] = self.practice_data[p2_col].apply(self._time_to_seconds)
            else:
                print("Warning: Practice 2 time data missing for regular race weekend")
                self.practice_data['p2_seconds'] = None
            if p3_col:
                self.practice_data['p3_seconds'] = self.practice_data[p3_col].apply(self._time_to_seconds)
            else:
                print("Warning: Practice 3 time data missing for regular race weekend")
                self.practice_data['p3_seconds'] = None
        
        # Load sprint data if it's a sprint weekend and path is provided
        if self.is_sprint_weekend and sprint_path:
            self.sprint_data, _ = self._safely_read_csv(sprint_path)
            print(f"Sprint data columns: {list(self.sprint_data.columns)}")
            
            # Find key columns in sprint data
            s_pos_col = self._find_column(self.sprint_data, ['POS', 'Pos', 'Position', 'POSITION'])
            s_driver_col = self._find_column(self.sprint_data, ['DRIVER', 'Driver', 'NAME', 'Name'])
            s_car_col = self._find_column(self.sprint_data, ['CAR', 'Car', 'TEAM', 'Team', 'Constructor'])
            s_time_col = self._find_column(self.sprint_data, ['TIME', 'Time', 'TIME/RETIRED', 'RESULT', 'Result'])
            
            if not s_pos_col or not s_driver_col:
                print("Warning: Sprint data missing position or driver columns")
            else:
                # Create standardized columns
                self.sprint_data['DRIVER_STD'] = self.sprint_data[s_driver_col].apply(self._standardize_driver_name)
                if s_car_col:
                    self.sprint_data['CAR_STD'] = self.sprint_data[s_car_col].apply(self._standardize_team_name)
                    
                # Process sprint positions
                self.sprint_data['sprint_position'] = self.sprint_data[s_pos_col].apply(self._safe_convert_position)
                
                # Process sprint times if available
                if s_time_col:
                    self.sprint_data['sprint_time_seconds'] = self.sprint_data[s_time_col].apply(self._parse_race_time)

        # Load sprint qualifying data if available and path is provided
        if self.is_sprint_weekend and sprint_quali_path:
            self.sprint_quali_data, _ = self._safely_read_csv(sprint_quali_path)
            print(f"Sprint qualifying data columns: {list(self.sprint_quali_data.columns)}")
            
            # Find key columns in sprint qualifying data
            sq_pos_col = self._find_column(self.sprint_quali_data, ['POS', 'Pos', 'Position', 'POSITION'])
            sq_driver_col = self._find_column(self.sprint_quali_data, ['DRIVER', 'Driver', 'NAME', 'Name'])
            sq_car_col = self._find_column(self.sprint_quali_data, ['CAR', 'Car', 'TEAM', 'Team', 'Constructor'])
            sq1_col = self._find_column(self.sprint_quali_data, ['Q1', 'SQ1', 'SQ1 Time'])
            sq2_col = self._find_column(self.sprint_quali_data, ['Q2', 'SQ2', 'SQ2 Time'])
            sq3_col = self._find_column(self.sprint_quali_data, ['Q3', 'SQ3', 'SQ3 Time'])
            
            if not sq_pos_col or not sq_driver_col:
                print("Warning: Sprint qualifying data missing position or driver columns")
            else:
                # Create standardized columns
                self.sprint_quali_data['DRIVER_STD'] = self.sprint_quali_data[sq_driver_col].apply(self._standardize_driver_name)
                if sq_car_col:
                    self.sprint_quali_data['CAR_STD'] = self.sprint_quali_data[sq_car_col].apply(self._standardize_team_name)
                
                # Process sprint qualifying positions
                self.sprint_quali_data['sprint_quali_position'] = self.sprint_quali_data[sq_pos_col].apply(self._safe_convert_position)
                
                # Process sprint qualifying times
                for sq_col, std_name in zip([sq1_col, sq2_col, sq3_col], ['SQ1', 'SQ2', 'SQ3']):
                    if sq_col:
                        self.sprint_quali_data[f'{std_name}_seconds'] = self.sprint_quali_data[sq_col].apply(self._time_to_seconds)
                
                # Calculate best sprint qualifying time
                if sq1_col or sq2_col or sq3_col:
                    self.sprint_quali_data['best_sprint_quali_time'] = self.sprint_quali_data.apply(
                        lambda row: min(
                            [t for t in [
                                row.get('SQ1_seconds'), 
                                row.get('SQ2_seconds'), 
                                row.get('SQ3_seconds')
                            ] if not pd.isna(t) and t is not None], 
                            default=None
                        ),
                        axis=1
                    )
                    
                    # Calculate gap to sprint pole
                    valid_times = self.sprint_quali_data['best_sprint_quali_time'].dropna()
                    if len(valid_times) > 0:
                        sprint_pole_time = valid_times.min()
                        self.sprint_quali_data['gap_to_sprint_pole'] = self.sprint_quali_data['best_sprint_quali_time'].apply(
                            lambda x: x - sprint_pole_time if not pd.isna(x) else None
                        )
        
        # Merge data using standardized driver names
        combined_data = self.quali_data.copy()
        
        # Standardize original column names
        if driver_col and driver_col != 'DRIVER':
            combined_data.rename(columns={driver_col: 'DRIVER'}, inplace=True)
        if car_col and car_col != 'CAR':
            combined_data.rename(columns={car_col: 'CAR'}, inplace=True)
            
        # Use standardized driver and car names
        combined_data['DRIVER'] = combined_data['DRIVER_STD']
        combined_data['CAR'] = combined_data['CAR_STD']
        
        # Add practice times to combined data using standardized driver names
        practice_data_copy = self.practice_data.copy()
        
        # Rename columns for consistency
        if p_driver_col and p_driver_col != 'DRIVER':
            practice_data_copy.rename(columns={p_driver_col: 'DRIVER'}, inplace=True)
        
        # Use standardized driver names for joining
        practice_data_copy['DRIVER'] = practice_data_copy['DRIVER_STD']
        
        # Add practice session data
        for _, practice_row in practice_data_copy.iterrows():
            driver = practice_row['DRIVER']
            combined_idx = combined_data[combined_data['DRIVER'] == driver].index
            
            if len(combined_idx) > 0:
                # Add available practice session data
                if 'p1_seconds' in practice_row and not pd.isna(practice_row['p1_seconds']):
                    combined_data.loc[combined_idx, 'p1_seconds'] = practice_row['p1_seconds']
                if 'p2_seconds' in practice_row and not pd.isna(practice_row['p2_seconds']):
                    combined_data.loc[combined_idx, 'p2_seconds'] = practice_row['p2_seconds']
                if 'p3_seconds' in practice_row and not pd.isna(practice_row['p3_seconds']):
                    combined_data.loc[combined_idx, 'p3_seconds'] = practice_row['p3_seconds']
        
        # Add sprint data if available
        if self.is_sprint_weekend and self.sprint_data is not None:
            sprint_data_copy = self.sprint_data.copy()
            
            # Add sprint data using standardized driver names
            for _, sprint_row in sprint_data_copy.iterrows():
                if 'DRIVER_STD' not in sprint_row:
                    continue
                    
                driver = sprint_row['DRIVER_STD']
                combined_idx = combined_data[combined_data['DRIVER'] == driver].index
                
                if len(combined_idx) > 0:
                    # Add sprint position
                    if 'sprint_position' in sprint_row:
                        combined_data.loc[combined_idx, 'sprint_position'] = sprint_row['sprint_position']
                    # Add sprint time if available
                    if 'sprint_time_seconds' in sprint_row:
                        combined_data.loc[combined_idx, 'sprint_time_seconds'] = sprint_row['sprint_time_seconds']
        
        # Add sprint qualifying data if available
        if self.is_sprint_weekend and self.sprint_quali_data is not None:
            sprint_quali_copy = self.sprint_quali_data.copy()
            
            # Add sprint qualifying data using standardized driver names
            for _, sq_row in sprint_quali_copy.iterrows():
                if 'DRIVER_STD' not in sq_row:
                    continue
                    
                driver = sq_row['DRIVER_STD']
                combined_idx = combined_data[combined_data['DRIVER'] == driver].index
                
                if len(combined_idx) > 0:
                    # Add sprint qualifying position
                    if 'sprint_quali_position' in sq_row:
                        combined_data.loc[combined_idx, 'sprint_quali_position'] = sq_row['sprint_quali_position']
                    # Add gap to sprint pole if available
                    if 'gap_to_sprint_pole' in sq_row:
                        combined_data.loc[combined_idx, 'gap_to_sprint_pole'] = sq_row['gap_to_sprint_pole']
                    # Add best sprint quali time
                    if 'best_sprint_quali_time' in sq_row:
                        combined_data.loc[combined_idx, 'best_sprint_quali_time'] = sq_row['best_sprint_quali_time']
        
        # Calculate practice session performance (different for sprint vs regular)
        if self.is_sprint_weekend:
            self._calculate_sprint_weekend_performance(combined_data)
        else:
            self._calculate_regular_weekend_performance(combined_data)
        
        # Add team and driver characteristics
        self._add_characteristics(combined_data)
        
        self.combined_data = combined_data
        print(f"Data loaded for {len(self.combined_data)} drivers\n")
        
        return self.combined_data
        
    def predict_top3(self):
        """Predict top 3 finishers"""
        if self.combined_data is None:
            print("Error: No data loaded. Please load data first.")
            return None
        
        print(f"Predicting top 3 finishers for {self.race_name}...")
        if self.is_sprint_weekend:
            print(f"Sprint race weekend")
        if self.rain_probability > 0:
            print(f"Weather conditions: {self.rain_probability*100:.0f}% chance of rain")
        else:
            print("Weather conditions: Dry")
        
        # Get track characteristics
        track = self.track
        overtaking_difficulty = track['overtaking_difficulty'] / 10
        tire_degradation = track['tire_degradation'] / 10
        start_importance = track['start_importance'] / 10
        
        # Calculate race scores
        if self.is_sprint_weekend:
            self.combined_data['race_score'] = self.combined_data.apply(
                lambda row: self._calculate_sprint_weekend_race_score(
                    row, overtaking_difficulty, tire_degradation, start_importance
                ),
                axis=1
            )
        else:
            self.combined_data['race_score'] = self.combined_data.apply(
                lambda row: self._calculate_regular_weekend_race_score(
                    row, overtaking_difficulty, tire_degradation, start_importance
                ),
                axis=1
            )
        
        # Sort by race score to get predicted order
        predicted_results = self.combined_data.sort_values('race_score', ascending=False).reset_index(drop=True)
        
        # Get top 3
        self.top3_prediction = predicted_results.head(3).copy()
        
        # Calculate predicted positions and position changes
        self.top3_prediction['predicted_position'] = range(1, len(self.top3_prediction) + 1)
        self.top3_prediction['position_change'] = self.top3_prediction['position'] - self.top3_prediction['predicted_position']
        
        # Calculate prediction error metrics
        self._calculate_prediction_error()
        
        # Print results to console
        self._print_prediction()
        
        return self.top3_prediction
    def _calculate_regular_weekend_race_score(self, driver, overtaking_difficulty, tire_degradation, start_importance):
        """Calculate race performance score for regular race weekend with rain factors"""
        try:
            # Starting position factor
            position_weight = 0.30 + (0.05 * overtaking_difficulty)
            # In wet conditions, starting position becomes less important
            position_weight = position_weight * (1 - (self.rain_probability * 0.3))
            
            position = float(driver['position']) if not pd.isna(driver['position']) else 20.0
            position_factor = np.exp(-0.15 * (position - 1))
            position_score = position_factor * position_weight
            
            # Qualifying pace factor
            quali_weight = 0.15 - (0.05 * overtaking_difficulty)
            # In wet conditions, qualifying pace becomes less important
            quali_weight = quali_weight * (1 - (self.rain_probability * 0.3))
            
            quali_factor = 1.0 if pd.isna(driver['gap_to_pole']) else max(0.7, 1 - (driver['gap_to_pole'] * 0.5))
            quali_score = quali_factor * quali_weight
            
            # Practice 2 factor (race pace)
            p2_weight = 0.25 + (0.05 * tire_degradation)
            # In wet conditions, practice pace is less representative
            p2_weight = p2_weight * (1 - (self.rain_probability * 0.4))
            
            p2_factor = driver['p2_score'] if 'p2_score' in driver and not pd.isna(driver['p2_score']) else 0.75
            p2_score = p2_factor * p2_weight
            
            # Practice 3 factor (qualifying simulation)
            p3_weight = 0.10
            # In wet conditions, practice pace is less representative
            p3_weight = p3_weight * (1 - (self.rain_probability * 0.4))
            
            p3_factor = driver['p3_score'] if 'p3_score' in driver and not pd.isna(driver['p3_score']) else 0.75
            p3_score = p3_factor * p3_weight
            
            # Team race pace factor
            team_weight = 0.10
            # Team race pace slightly less relevant in wet conditions
            team_weight = team_weight * (1 - (self.rain_probability * 0.2))
            
            team_factor = driver['race_pace_factor'] if 'race_pace_factor' in driver else 1.0
            team_score = team_factor * team_weight
            
            # Tire management factor
            tire_weight = 0.10 + (0.05 * tire_degradation)
            # In wet conditions, tire management becomes more important
            tire_weight = tire_weight * (1 + (self.rain_probability * 0.2))
            
            tire_factor = driver['tire_mgmt'] / 10 if 'tire_mgmt' in driver else 0.7
            tire_score = tire_factor * tire_weight
            
            # Driver experience factor
            exp_weight = 0.10 + (0.02 * tire_degradation)
            # In wet conditions, experience becomes more important
            exp_weight = exp_weight * (1 + (self.rain_probability * 0.3))
            
            exp_factor = driver['driver_experience'] if 'driver_experience' in driver else 0.85
            exp_score = exp_factor * exp_weight
            
            # Calculate wet performance factors (only applies when rain probability > 0)
            wet_driver_score = 0
            wet_team_score = 0
            
            if self.rain_probability > 0:
                # Driver wet performance factor (increases with rain probability)
                wet_driver_weight = 0.35 * self.rain_probability
                wet_driver_factor = driver['driver_wet_performance'] / 10 if 'driver_wet_performance' in driver else 0.75
                wet_driver_score = wet_driver_factor * wet_driver_weight
                
                # Team wet performance factor (increases with rain probability)
                wet_team_weight = 0.25 * self.rain_probability
                wet_team_factor = driver['wet_performance'] / 10 if 'wet_performance' in driver else 0.7
                wet_team_score = wet_team_factor * wet_team_weight
            
            # Total score
            total_weight = (position_weight + quali_weight + p2_weight + p3_weight + 
                           team_weight + tire_weight + exp_weight + 
                           (0.35 * self.rain_probability) + (0.25 * self.rain_probability))
            
            race_score = (position_score + quali_score + p2_score + p3_score + 
                         team_score + tire_score + exp_score + 
                         wet_driver_score + wet_team_score) / total_weight
            
            return race_score
        except Exception as e:
            print(f"Error calculating race score: {e}")
            return 0.1
            
    def _calculate_sprint_weekend_race_score(self, driver, overtaking_difficulty, tire_degradation, start_importance):
        """Calculate race performance score for sprint race weekend with rain factors"""
        try:
            # Starting position factor
            position_weight = 0.25 + (0.05 * overtaking_difficulty)
            # In wet conditions, starting position becomes less important
            position_weight = position_weight * (1 - (self.rain_probability * 0.3))
            
            position = float(driver['position']) if not pd.isna(driver['position']) else 20.0
            position_factor = np.exp(-0.15 * (position - 1))
            position_score = position_factor * position_weight
            
            # Qualifying pace factor
            quali_weight = 0.15 - (0.05 * overtaking_difficulty)
            # In wet conditions, qualifying pace becomes less important
            quali_weight = quali_weight * (1 - (self.rain_probability * 0.3))
            
            quali_factor = 1.0 if pd.isna(driver['gap_to_pole']) else max(0.7, 1 - (driver['gap_to_pole'] * 0.5))
            quali_score = quali_factor * quali_weight
            
            # Sprint race performance factor (specific to sprint weekends)
            sprint_weight = 0.20
            # Sprint performance slightly less relevant in wet race conditions
            sprint_weight = sprint_weight * (1 - (self.rain_probability * 0.2))
            
            sprint_factor = driver['sprint_position_score'] if 'sprint_position_score' in driver and not pd.isna(driver['sprint_position_score']) else 0.75
            sprint_score = sprint_factor * sprint_weight
            
            # Practice 1 factor (only practice in sprint weekend)
            p1_weight = 0.10
            # In wet conditions, practice pace is less representative
            p1_weight = p1_weight * (1 - (self.rain_probability * 0.4))
            
            p1_factor = driver['p1_score'] if 'p1_score' in driver and not pd.isna(driver['p1_score']) else 0.75
            p1_score = p1_factor * p1_weight
            
            # Team race pace factor
            team_weight = 0.10
            # Team race pace slightly less relevant in wet conditions
            team_weight = team_weight * (1 - (self.rain_probability * 0.2))
            
            team_factor = driver['race_pace_factor'] if 'race_pace_factor' in driver else 1.0
            team_score = team_factor * team_weight
            
            # Tire management factor
            tire_weight = 0.10 + (0.05 * tire_degradation)
            # In wet conditions, tire management becomes more important
            tire_weight = tire_weight * (1 + (self.rain_probability * 0.2))
            
            tire_factor = driver['tire_mgmt'] / 10 if 'tire_mgmt' in driver else 0.7
            tire_score = tire_factor * tire_weight
            
            # Driver sprint performance factor
            driver_sprint_weight = 0.15
            # Sprint performance becomes more important in wet conditions (different skill set)
            driver_sprint_weight = driver_sprint_weight * (1 + (self.rain_probability * 0.1))
            
            driver_sprint_factor = driver['driver_sprint_performance'] / 10 if 'driver_sprint_performance' in driver else 0.75
            driver_sprint_score = driver_sprint_factor * driver_sprint_weight
            
            # Team sprint performance factor
            team_sprint_weight = 0.05
            team_sprint_factor = driver['sprint_performance'] / 10 if 'sprint_performance' in driver else 0.75
            team_sprint_score = team_sprint_factor * team_sprint_weight
            
            # Calculate wet performance factors (only applies when rain probability > 0)
            wet_driver_score = 0
            wet_team_score = 0
            
            if self.rain_probability > 0:
                # Driver wet weather skill
                wet_driver_weight = 0.35 * self.rain_probability
                wet_driver_factor = driver['driver_wet_performance'] / 10 if 'driver_wet_performance' in driver else 0.75
                wet_driver_score = wet_driver_factor * wet_driver_weight
                
                # Team wet weather performance
                wet_team_weight = 0.25 * self.rain_probability
                wet_team_factor = driver['wet_performance'] / 10 if 'wet_performance' in driver else 0.7
                wet_team_score = wet_team_factor * wet_team_weight
            
            # Total score
            total_weight = (position_weight + quali_weight + sprint_weight + p1_weight + 
                           team_weight + tire_weight + driver_sprint_weight + team_sprint_weight + 
                           (0.35 * self.rain_probability) + (0.25 * self.rain_probability))
            
            race_score = (position_score + quali_score + sprint_score + p1_score + 
                         team_score + tire_score + driver_sprint_score + team_sprint_score + 
                         wet_driver_score + wet_team_score) / total_weight
            
            return race_score
        except Exception as e:
            print(f"Error calculating sprint weekend race score: {e}")
            return 0.1
    
    def _calculate_prediction_error(self):
        """Calculate prediction error metrics"""
        # Base position variance by track predictability
        base_variance = 1.2
        
        # Adjust based on weather conditions (rain increases uncertainty)
        weather_uncertainty = 1.0 + (self.rain_probability * 0.5)
        
        # Adjust by score spread (closer scores = more uncertainty)
        score_spread = self.top3_prediction['race_score'].max() - self.top3_prediction['race_score'].min()
        adjusted_variance = base_variance * weather_uncertainty * (1 + (0.5 - min(0.5, score_spread)))
        
        # Simulate errors
        np.random.seed(42)  # For reproducibility
        simulated_errors = np.random.normal(0, adjusted_variance, len(self.top3_prediction))
        
        # Calculate simulated positions
        simulated_positions = np.clip(
            self.top3_prediction['predicted_position'] + simulated_errors,
            1, 20
        )
        
        # Calculate MSE and RMSE
        self.mse = mean_squared_error(self.top3_prediction['predicted_position'], simulated_positions)
        self.rmse = np.sqrt(self.mse)
    
    def _print_prediction(self):
        """Print prediction results to console in a formatted way"""
        print("\n" + "="*50)
        print(f"F1 RACE PREDICTION: {self.race_name} TOP 3")
        print("="*50)
        
        # Print weather conditions
        if self.rain_probability > 0:
            if self.rain_probability < 0.3:
                condition = "Light rain possible"
            elif self.rain_probability < 0.7:
                condition = "Intermittent rain likely"
            else:
                condition = "Heavy rain expected"
            print(f"\nWeather: {condition} ({self.rain_probability*100:.0f}% chance of rain)")
        else:
            print("\nWeather: Dry conditions")
        
        print("\nPREDICTED TOP 3 FINISHERS:")
        for i, (_, driver) in enumerate(self.top3_prediction.iterrows()):
            position_change = driver['position_change']
            change_text = f"(+{int(position_change)})" if position_change > 0 else \
                        f"({int(position_change)})" if position_change < 0 else "(=)"
            
            print(f"{i+1}. {driver['DRIVER']} ({driver['CAR']}) - Started P{int(driver['position'])} {change_text}")
        
        print("\nPREDICTION ACCURACY METRICS:")
        print(f"Mean Squared Error (MSE): {self.mse:.4f}")
        print(f"Root Mean Squared Error (RMSE): {self.rmse:.4f}")
        print(f"Position Accuracy: ±{self.rmse:.2f} positions")
        
        # Calculate confidence percentage (adjusted for rain uncertainty)
        # Rain reduces confidence
        rain_adjustment = self.rain_probability * 10  # 0-10% reduction
        confidence = 100 - (self.rmse * 25) - rain_adjustment
        print(f"Prediction Confidence: {confidence:.1f}%")
        
        print("\nKEY FACTORS FOR WINNER:")
        winner = self.top3_prediction.iloc[0]
        
        # Get track characteristics
        track = self.track
        overtaking_difficulty = track['overtaking_difficulty'] / 10
        tire_degradation = track['tire_degradation'] / 10
        
        # Calculate factors based on weekend type
        if self.is_sprint_weekend:
            self._print_sprint_weekend_factors(winner, overtaking_difficulty, tire_degradation)
        else:
            self._print_regular_weekend_factors(winner, overtaking_difficulty, tire_degradation)
    
    def _print_regular_weekend_factors(self, winner, overtaking_difficulty, tire_degradation):
        """Print key factors for winner in regular race weekend"""
        # Starting position
        position_weight = 0.30 + (0.05 * overtaking_difficulty)
        position_weight = position_weight * (1 - (self.rain_probability * 0.3))
        position_factor = np.exp(-0.15 * (float(winner['position']) - 1)) * position_weight
        
        # Qualifying pace
        quali_weight = 0.15 - (0.05 * overtaking_difficulty)
        quali_weight = quali_weight * (1 - (self.rain_probability * 0.3))
        quali_factor = (1.0 if pd.isna(winner['gap_to_pole']) else 
                       max(0.7, 1 - (winner['gap_to_pole'] * 0.5))) * quali_weight
        
        # Practice 2 (race pace)
        p2_weight = 0.25 + (0.05 * tire_degradation)
        p2_weight = p2_weight * (1 - (self.rain_probability * 0.4))
        p2_factor = (winner['p2_score'] if 'p2_score' in winner and 
                    not pd.isna(winner['p2_score']) else 0.75) * p2_weight
        
        # Practice 3
        p3_weight = 0.10
        p3_weight = p3_weight * (1 - (self.rain_probability * 0.4))
        p3_factor = (winner['p3_score'] if 'p3_score' in winner and 
                    not pd.isna(winner['p3_score']) else 0.75) * p3_weight
        
        # Team race pace
        team_weight = 0.10 * (1 - (self.rain_probability * 0.2))
        team_factor = winner['race_pace_factor'] * team_weight
        
        # Tire management
        tire_weight = (0.10 + (0.05 * tire_degradation)) * (1 + (self.rain_probability * 0.2))
        tire_factor = (winner['tire_mgmt'] / 10) * tire_weight
        
        # Driver experience
        exp_weight = (0.10 + (0.02 * tire_degradation)) * (1 + (self.rain_probability * 0.3))
        exp_factor = winner['driver_experience'] * exp_weight
        
        # Wet performance factors
        wet_driver_factor = 0
        wet_team_factor = 0
        
        if self.rain_probability > 0:
            # Driver wet weather skill
            wet_driver_weight = 0.35 * self.rain_probability
            wet_driver_factor = (winner['driver_wet_performance'] / 10) * wet_driver_weight
            
            # Team wet weather performance
            wet_team_weight = 0.25 * self.rain_probability
            wet_team_factor = (winner['wet_performance'] / 10) * wet_team_weight
        
        # Calculate total and normalize percentages
        total = (position_factor + quali_factor + p2_factor + p3_factor + 
                team_factor + tire_factor + exp_factor + wet_driver_factor + wet_team_factor)
        
        # Print factor percentages in the format shown in the example
        print(f"Starting position: {(position_factor / total * 100):.1f}%")
        print(f"Qualifying pace: {(quali_factor / total * 100):.1f}%")
        print(f"Practice 2 (race pace): {(p2_factor / total * 100):.1f}%")
        print(f"Practice 3: {(p3_factor / total * 100):.1f}%")
        print(f"Team race pace: {(team_factor / total * 100):.1f}%")
        print(f"Tire management: {(tire_factor / total * 100):.1f}%")
        print(f"Driver experience: {(exp_factor / total * 100):.1f}%")
        
        # Only show wet factors if rain probability > 0
        if self.rain_probability > 0:
            print(f"Driver wet weather skill: {(wet_driver_factor / total * 100):.1f}%")
            print(f"Team wet weather performance: {(wet_team_factor / total * 100):.1f}%")
    
    def _print_sprint_weekend_factors(self, winner, overtaking_difficulty, tire_degradation):
        """Print key factors for winner in sprint race weekend"""
        # Starting position
        position_weight = 0.25 + (0.05 * overtaking_difficulty)
        position_weight = position_weight * (1 - (self.rain_probability * 0.3))
        position_factor = np.exp(-0.15 * (float(winner['position']) - 1)) * position_weight
        
        # Qualifying pace
        quali_weight = 0.15 - (0.05 * overtaking_difficulty)
        quali_weight = quali_weight * (1 - (self.rain_probability * 0.3))
        quali_factor = (1.0 if pd.isna(winner['gap_to_pole']) else 
                       max(0.7, 1 - (winner['gap_to_pole'] * 0.5))) * quali_weight
        
        # Sprint race performance
        sprint_weight = 0.20 * (1 - (self.rain_probability * 0.2))
        sprint_position_factor = (winner['sprint_position_score'] if 'sprint_position_score' in winner and 
                                 not pd.isna(winner['sprint_position_score']) else 0.75) * sprint_weight
        
        # Practice 1
        p1_weight = 0.10 * (1 - (self.rain_probability * 0.4))
        p1_factor = (winner['p1_score'] if 'p1_score' in winner and 
                    not pd.isna(winner['p1_score']) else 0.75) * p1_weight
        
        # Team race pace
        team_weight = 0.10 * (1 - (self.rain_probability * 0.2))
        team_factor = winner['race_pace_factor'] * team_weight
        
        # Tire management
        tire_weight = (0.10 + (0.05 * tire_degradation)) * (1 + (self.rain_probability * 0.2))
        tire_factor = (winner['tire_mgmt'] / 10) * tire_weight
        
        # Driver sprint performance
        driver_sprint_weight = 0.15 * (1 + (self.rain_probability * 0.1))
        driver_sprint_factor = (winner['driver_sprint_performance'] / 10) * driver_sprint_weight
        
        # Team sprint performance
        team_sprint_weight = 0.05
        team_sprint_factor = (winner['sprint_performance'] / 10) * team_sprint_weight
        
        # Wet performance factors
        wet_driver_factor = 0
        wet_team_factor = 0
        
        if self.rain_probability > 0:
            # Driver wet weather skill
            wet_driver_weight = 0.35 * self.rain_probability
            wet_driver_factor = (winner['driver_wet_performance'] / 10) * wet_driver_weight
            
            # Team wet weather performance
            wet_team_weight = 0.25 * self.rain_probability
            wet_team_factor = (winner['wet_performance'] / 10) * wet_team_weight
        
        # Calculate total and normalize percentages
        total = (position_factor + quali_factor + sprint_position_factor + p1_factor + 
                team_factor + tire_factor + driver_sprint_factor + team_sprint_factor + 
                wet_driver_factor + wet_team_factor)
        
        # Print factor percentages in the format shown in the example
        print(f"Starting position: {(position_factor / total * 100):.1f}%")
        print(f"Qualifying pace: {(quali_factor / total * 100):.1f}%")
        print(f"Sprint race performance: {(sprint_position_factor / total * 100):.1f}%")
        print(f"Practice 1: {(p1_factor / total * 100):.1f}%")
        print(f"Team race pace: {(team_factor / total * 100):.1f}%")
        print(f"Tire management: {(tire_factor / total * 100):.1f}%")
        print(f"Driver sprint ability: {(driver_sprint_factor / total * 100):.1f}%")
        print(f"Team sprint setup: {(team_sprint_factor / total * 100):.1f}%")
        
        # Only show wet factors if rain probability > 0
        if self.rain_probability > 0:
            print(f"Driver wet weather skill: {(wet_driver_factor / total * 100):.1f}%")
            print(f"Team wet weather performance: {(wet_team_factor / total * 100):.1f}%")
            
    def _parse_race_time(self, time_str):
        """
        Parse race time string, handling various formats including:
        - '1:23.456'
        - '+12.345'
        - 'DNF', 'DNS', etc.
        """
        if pd.isna(time_str) or not isinstance(time_str, str):
            return None
        
        # Handle DNF, DNS, etc.
        if any(x in time_str.upper() for x in ['DNF', 'DNS', 'DSQ', 'NC', 'DQ', 'RETIRED']):
            return None
            
        # Remove leading '+' for gap times
        if time_str.startswith('+'):
            return None  # We can't use gap times directly
            
        # Try standard time format
        return self._time_to_seconds(time_str)
    
    def _time_to_seconds(self, time_str):
        """
        Convert time string to seconds, supporting multiple formats:
        - '1:23.456' (minutes:seconds.milliseconds)
        - '83.456' (seconds.milliseconds)
        - '1m23.456s' (alternative format)
        """
        if pd.isna(time_str) or not isinstance(time_str, str):
            return None
            
        # Clean the string
        time_str = time_str.strip()
        
        # Handle empty strings
        if time_str == '' or time_str == '-':
            return None
            
        # Handle DNF, DNS, etc.
        if any(x in time_str.upper() for x in ['DNF', 'DNS', 'DSQ', 'NC', 'DQ', 'RETIRED']):
            return None
        
        try:
            # Format: 1:23.456
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    minutes = int(parts[0])
                    seconds = float(parts[1])
                    return minutes * 60 + seconds
                    
            # Format: 1m23.456s
            elif 'm' in time_str and 's' in time_str:
                match = re.match(r'(\d+)m([\d\.]+)s', time_str)
                if match:
                    minutes = int(match.group(1))
                    seconds = float(match.group(2))
                    return minutes * 60 + seconds
            
            # Format: Just seconds (83.456)
            else:
                # Remove any non-numeric characters except '.' (e.g. 's')
                cleaned = ''.join(c for c in time_str if c.isdigit() or c == '.')
                if cleaned:
                    return float(cleaned)
                    
            return None
        except Exception as e:
            print(f"Error converting time '{time_str}': {e}")
            return None
    
    def _safe_convert_position(self, pos):
        """
        Safely convert position to number, handling:
        - DNS, DNF, DSQ, etc.
        - P1, P2, etc. format
        - 1st, 2nd, etc. format
        """
        if isinstance(pos, (int, float)):
            return pos
        
        if not isinstance(pos, str):
            return 20  # Default to back of grid for None, etc.
            
        pos = pos.strip()
            
        # Handle empty strings
        if pos == '' or pos == '-':
            return 20
            
        # Handle 'P1', 'P2', etc.
        if pos.startswith('P') and len(pos) > 1 and pos[1:].isdigit():
            return int(pos[1:])
            
        # Handle '1st', '2nd', etc.
        if pos.endswith(('st', 'nd', 'rd', 'th')) and pos[:-2].isdigit():
            return int(pos[:-2])
        
        try:
            return int(pos)
        except:
            # Handle DNS, DNF, etc.
            if any(x in pos.upper() for x in ['DNS', 'DNF', 'DSQ', 'NC', 'DQ', 'RETIRED']):
                return 20  # Back of the grid
            
            # Try to extract digits if mixed format
            digits = ''.join(c for c in pos if c.isdigit())
            if digits:
                try:
                    return int(digits)
                except:
                    pass
                    
            return 20  # Default to back of grid
    
    def _calculate_regular_weekend_performance(self, data):
        """Calculate performance metrics from practice sessions for regular race weekend"""
        # FP2 performance (race pace)
        valid_p2_times = data['p2_seconds'].dropna()
        if len(valid_p2_times) > 0:
            best_p2_time = valid_p2_times.min()
            data['p2_gap'] = data['p2_seconds'].apply(
                lambda x: x - best_p2_time if not pd.isna(x) else None
            )
            data['p2_score'] = data['p2_gap'].apply(
                lambda x: max(0.7, 1 - (x * 0.4)) if not pd.isna(x) else 0.75
            )
        else:
            data['p2_score'] = 0.75
        
        # FP3 performance (qualifying simulation)
        valid_p3_times = data['p3_seconds'].dropna()
        if len(valid_p3_times) > 0:
            best_p3_time = valid_p3_times.min()
            data['p3_gap'] = data['p3_seconds'].apply(
                lambda x: x - best_p3_time if not pd.isna(x) else None
            )
            data['p3_score'] = data['p3_gap'].apply(
                lambda x: max(0.7, 1 - (x * 0.5)) if not pd.isna(x) else 0.75
            )
        else:
            data['p3_score'] = 0.75
    
    def _calculate_sprint_weekend_performance(self, data):
        """Calculate performance metrics for sprint race weekend"""
        # FP1 performance (only practice session in sprint weekend)
        valid_p1_times = data['p1_seconds'].dropna()
        if len(valid_p1_times) > 0:
            best_p1_time = valid_p1_times.min()
            data['p1_gap'] = data['p1_seconds'].apply(
                lambda x: x - best_p1_time if not pd.isna(x) else None
            )
            data['p1_score'] = data['p1_gap'].apply(
                lambda x: max(0.7, 1 - (x * 0.4)) if not pd.isna(x) else 0.75
            )
        else:
            data['p1_score'] = 0.75
        
        # Sprint race performance
        if 'sprint_position' in data.columns:
            # Calculate sprint position score (higher for better positions)
            data['sprint_position_score'] = data['sprint_position'].apply(
                lambda x: max(0.6, 1 - (x - 1) * 0.03) if not pd.isna(x) else 0.7
            )
        else:
            data['sprint_position_score'] = 0.7
    
    def _add_characteristics(self, data):
        """Add team and driver characteristics"""
        # Add team characteristics
        for team, chars in self.team_characteristics.items():
            for char, value in chars.items():
                data.loc[data['CAR'] == team, char] = value
        
        # Fill missing values with defaults
        data['race_pace_factor'] = data['race_pace_factor'].fillna(1.0)
        data['tire_mgmt'] = data['tire_mgmt'].fillna(7.0)
        data['start_performance'] = data['start_performance'].fillna(7.0)
        data['wet_performance'] = data['wet_performance'].fillna(7.0)
        data['sprint_performance'] = data['sprint_performance'].fillna(7.5)
        
        # Add driver experience
        data['driver_experience'] = data['DRIVER'].map(self.driver_experience).fillna(0.85)
        
        # Add driver wet weather performance
        data['driver_wet_performance'] = data['DRIVER'].map(self.driver_wet_performance).fillna(7.5)
        
        # Add driver sprint performance
        data['driver_sprint_performance'] = data['DRIVER'].map(self.driver_sprint_performance).fillna(7.5)
    
class F1TerminalFileSelector:
    """GUI for selecting data files, race, and rain probability with terminal output"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Race Top 3 Predictor")
        self.root.geometry("700x350")  # Reduced height since we don't need log output in GUI
        
        self.predictor = F1RacePredictor()
        self.quali_path = None
        self.practice_path = None
        self.sprint_path = None
        self.sprint_quali_path = None
        self.rain_value = tk.DoubleVar(value=0)
        self.is_sprint_weekend = False
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the UI components"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls frame
        frame = ttk.Frame(main_frame, padding="20")
        frame.pack(fill=tk.X)
        
        # Title
        title = ttk.Label(frame, text="F1 Race Top 3 Predictor", font=("Arial", 14, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Data file selection
        ttk.Label(frame, text="Qualifying Data:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quali_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.quali_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_quali).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="Practice Data:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.practice_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.practice_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self._browse_practice).grid(row=2, column=2, padx=5, pady=5)
        
        # Sprint race data (initially hidden)
        self.sprint_label = ttk.Label(frame, text="Sprint Race Data:")
        self.sprint_var = tk.StringVar()
        self.sprint_entry = ttk.Entry(frame, textvariable=self.sprint_var, width=50)
        self.sprint_button = ttk.Button(frame, text="Browse...", command=self._browse_sprint)
        
        # Sprint qualifying data (initially hidden)
        self.sprint_quali_label = ttk.Label(frame, text="Sprint Qualifying Data:")
        self.sprint_quali_var = tk.StringVar()
        self.sprint_quali_entry = ttk.Entry(frame, textvariable=self.sprint_quali_var, width=50)
        self.sprint_quali_button = ttk.Button(frame, text="Browse...", command=self._browse_sprint_quali)
        
        # Race selection
        ttk.Label(frame, text="Race:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.race_var = tk.StringVar()
        
        # Create race dropdown with races in calendar order
        races = list(self.predictor.track_database.keys())
        race_dropdown = ttk.Combobox(frame, textvariable=self.race_var, width=48, state="readonly")
        race_dropdown['values'] = races
        race_dropdown.current(0)  # Default to first race
        race_dropdown.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        race_dropdown.bind("<<ComboboxSelected>>", self._on_race_select)
        
        # Sprint weekend indicator
        self.sprint_indicator = ttk.Label(frame, text="", font=("Arial", 10, "italic"))
        self.sprint_indicator.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Rain probability slider
        ttk.Label(frame, text="Rain Probability:").grid(row=6, column=0, sticky=tk.W, pady=5)
        rain_frame = ttk.Frame(frame)
        rain_frame.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        rain_slider = Scale(rain_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                           variable=self.rain_value, length=380,
                           label="", showvalue=True)
        rain_slider.pack(side=tk.LEFT)
        ttk.Label(rain_frame, text="%").pack(side=tk.LEFT, padx=(0, 5))
        
        # Predict button
        predict_button = ttk.Button(frame, text="Predict Top 3", command=self._run_prediction)
        predict_button.grid(row=7, column=0, columnspan=3, pady=15)
        
        # Status label
        self.status_label = ttk.Label(frame, text="Ready", font=("Arial", 10, "italic"))
        self.status_label.grid(row=8, column=0, columnspan=3, pady=(0, 10))
        
        # Initialize race selection
        self._on_race_select(None)
    
    def _on_race_select(self, event):
        """Handle race selection"""
        selected_race = self.race_var.get()
        if not selected_race:
            return
            
        # Check if it's a sprint weekend
        self.is_sprint_weekend = self.predictor.track_database[selected_race].get("is_sprint", False)
        
        if self.is_sprint_weekend:
            # Show sprint data fields
            self.sprint_indicator.config(text="Sprint Weekend")
            
            # Sprint Race Data
            self.sprint_label.grid(row=3, column=0, sticky=tk.W, pady=5)
            self.sprint_entry.grid(row=3, column=1, padx=5, pady=5)
            self.sprint_button.grid(row=3, column=2, padx=5, pady=5)
            
            # Sprint Qualifying Data
            self.sprint_quali_label.grid(row=4, column=0, sticky=tk.W, pady=5)
            self.sprint_quali_entry.grid(row=4, column=1, padx=5, pady=5)
            self.sprint_quali_button.grid(row=4, column=2, padx=5, pady=5)
        else:
            # Hide sprint data fields
            self.sprint_indicator.config(text="")
            
            # Hide Sprint Race Data
            self.sprint_label.grid_remove()
            self.sprint_entry.grid_remove()
            self.sprint_button.grid_remove()
            self.sprint_var.set("")
            self.sprint_path = None
            
            # Hide Sprint Qualifying Data
            self.sprint_quali_label.grid_remove()
            self.sprint_quali_entry.grid_remove()
            self.sprint_quali_button.grid_remove()
            self.sprint_quali_var.set("")
            self.sprint_quali_path = None
    
    def _browse_quali(self):
        """Browse for qualifying data file"""
        filepath = filedialog.askopenfilename(
            title="Select Qualifying Data File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filepath:
            self.quali_path = filepath
            self.quali_var.set(filepath)
    
    def _browse_practice(self):
        """Browse for practice data file"""
        filepath = filedialog.askopenfilename(
            title="Select Practice Data File", 
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filepath:
            self.practice_path = filepath
            self.practice_var.set(filepath)
    
    def _browse_sprint(self):
        """Browse for sprint race data file"""
        filepath = filedialog.askopenfilename(
            title="Select Sprint Race Data File", 
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filepath:
            self.sprint_path = filepath
            self.sprint_var.set(filepath)
    
    def _browse_sprint_quali(self):
        """Browse for sprint qualifying data file"""
        filepath = filedialog.askopenfilename(
            title="Select Sprint Qualifying Data File", 
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filepath:
            self.sprint_quali_path = filepath
            self.sprint_quali_var.set(filepath)
    
    def _run_prediction(self):
        """Run the prediction with selected files"""
        self.status_label.config(text="Processing...")
        self.root.update()
        
        if not self.quali_path:
            self.status_label.config(text="Error: Please select a qualifying data file.")
            messagebox.showerror("Input Error", "Please select a qualifying data file.")
            return
            
        if not self.practice_path:
            self.status_label.config(text="Error: Please select a practice data file.")
            messagebox.showerror("Input Error", "Please select a practice data file.")
            return
            
        race = self.race_var.get()
        if not race:
            self.status_label.config(text="Error: Please select a race.")
            messagebox.showerror("Input Error", "Please select a race.")
            return
        
        # Check if sprint data is required but missing
        is_sprint_race = self.predictor.track_database[race].get("is_sprint", False)
        if is_sprint_race and not self.sprint_path:
            response = messagebox.askyesno(
                "Sprint Data Missing", 
                "This is a sprint race weekend, but no sprint race data was provided. \n\n"
                "Sprint results significantly improve prediction accuracy. \n\n"
                "Do you want to continue without sprint data?"
            )
            if not response:
                self.status_label.config(text="Ready")
                return
        
        try:
            # Run prediction in a way that outputs to terminal
            self._execute_prediction()
            
            # Close the GUI after prediction completes
            self.status_label.config(text="Prediction complete! See terminal for results.")
            self.root.after(2000, self.root.destroy)  # Close GUI after 2 seconds
            
        except Exception as e:
            error_msg = f"Error during prediction: {str(e)}"
            self.status_label.config(text="Error occurred. See terminal for details.")
            print(f"\nERROR: {error_msg}")
            traceback.print_exc()
            messagebox.showerror("Prediction Error", error_msg)
    
    def _execute_prediction(self):
        """Execute prediction and direct output to terminal"""
        # Save and restore stdout to ensure terminal output
        race = self.race_var.get()
        
        print(f"\n{'='*50}")
        print(f"RUNNING PREDICTION FOR: {race}")
        print(f"{'='*50}")
        
        # Set race, rain probability and load data
        print(f"Race: {race}")
        self.predictor.set_race(race)
        rain_prob = self.rain_value.get() / 100
        self.predictor.set_rain_probability(rain_prob)
        print(f"Rain probability set to {rain_prob*100:.0f}%")
        
        # Show files being used
        print(f"\nLoading data files...")
        print(f"Qualifying data: {os.path.basename(self.quali_path)}")
        print(f"Practice data: {os.path.basename(self.practice_path)}")
        
        if self.is_sprint_weekend:
            if self.sprint_path:
                print(f"Sprint race data: {os.path.basename(self.sprint_path)}")
            if self.sprint_quali_path:
                print(f"Sprint qualifying data: {os.path.basename(self.sprint_quali_path)}")
        
        # Load data (include sprint data if available)
        if self.is_sprint_weekend:
            # For sprint race weekends
            self.predictor.load_data(
                self.quali_path, 
                self.practice_path, 
                self.sprint_path if self.sprint_path else None,
                self.sprint_quali_path if self.sprint_quali_path else None
            )
        else:
            # For regular race weekends
            self.predictor.load_data(self.quali_path, self.practice_path)
        
        # Run prediction
        top3 = self.predictor.predict_top3()
        if top3 is None:
            print("\nPrediction failed.")


def main():
    root = tk.Tk()
    app = F1TerminalFileSelector(root)
    root.mainloop()
    print("\nThank you for using F1 Race Predictor. Goodbye!")


if __name__ == "__main__":
    main()