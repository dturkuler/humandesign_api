from .. import hd_constants
import swisseph  as swe  
from IPython.display import display
import pandas as pd
import numpy as np
import itertools
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pytz import timezone
from multiprocessing import Pool
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import sys

def get_inc_cross(date_to_gate_dict):
    ''' 
    get incarnation cross from open gates 
        Args:
            date_to_gate_dict(dict):output of hd_feature class 
                                    keys->[planets,label,longitude,gate,line,color,tone,base]
        Return:
            incarnation cross(tuple): gates of sun and earth from birth and create date 
                                      format e.g. ((1,2),(3,4))
    '''
    df = date_to_gate_dict
    idx = int(len(df["planets"])/2) #start idx of design values 
    inc_cross = (
        (df["gate"][0],df["gate"][1]),#sun&earth gate at birth
        (df["gate"][idx],df["gate"][idx+1])#sun&earth gate at design
                )          
    profile = df["line"][0],df["line"][idx]
    cr_typ = hd_constants.IC_CROSS_TYP[profile]
    inc_cross = str(inc_cross)+"-"+cr_typ
    return inc_cross

def get_profile(date_to_gate_dict):
    ''' 
    profile is calculated from sun line of birth and design date
    Args:
        date_to_gate_dict(dict):output of hd_feature class 
                                    keys->[planets,label,longitude,gate,line,color,tone,base]
    Return:
        profile(tuple): format e.g. (1,4)
    '''
    df = date_to_gate_dict
    idx = int(len(df["line"])/2) #start idx of design values
    profile = (df["line"][0],df["line"][idx]) #sun gate at birth and design
    #sort lines to known format
    if profile not in hd_constants.IC_CROSS_TYP.keys():
        profile = profile[::-1]
    
    return profile

def get_variables(date_to_gate_dict):
    '''
    variables are calculated based on tones of sun(birth,design) and 
    Nodes(birth,design), respectively
    If tone 1,2,3-> left arrow, else right arrow
    Args:
        date_to_gate_dict(dict):output of hd_feature class 
                                    keys->[planets,label,longitude,gate,line,color,tone,base]
    Return:
        variables(dict): keys-> ["right_up","right_down","left_up","left_down"]
    '''
    df = date_to_gate_dict
    idx = int(len(df["tone"])/2) #start idx of design values 
    tones = (
            (df["tone"][0]),#sun at birth
            (df["tone"][3]),#Node at birth
            (df["tone"][idx]),#sun at design
            (df["tone"][idx+3]),#node at design
                ) 
    keys = ["right_up","right_down","left_up","left_down"] #arrows,variables
    variables = {keys[idx]:"left" if tone<=3 else "right" for idx,tone in enumerate(tones)}

    return variables 

