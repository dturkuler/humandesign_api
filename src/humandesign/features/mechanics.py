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

def is_connected(active_channels_dict, *args):
    ''' 
    get bool answer wheater chakras are connected through channel or not
    direct and indirekt connections are supported (e.g ["TT","AA"],["TT","SN","RT"])
    Checks if the chakras in *args form a connected path in the order provided.
        Params: 
           active_channels_dict(dict): all active channels, keys: ["label","planets","gate","ch_gate"]
           *args(str): sequence of Chakras that will be checked for connection                                    
    Return:
        bool: returns True if connected in sequence, and false if not
    '''
    #if gate list is emtpy ->Reflector-Typ (no channels at all), return false
    if not len(active_channels_dict["gate"]):
        return False
        
    gate_chakras = active_channels_dict["gate_chakra"]
    ch_gate_chakras = active_channels_dict["ch_gate_chakra"]
    
    # Check each link in the path
    for i in range(len(args) - 1):
        c1 = args[i]
        c2 = args[i+1]
        
        # Check if any active channel connects c1 and c2
        connected = False
        # iterate through all active channels to find a match
        for gc, cgc in zip(gate_chakras, ch_gate_chakras):
            if (gc == c1 and cgc == c2) or (gc == c2 and cgc == c1):
                connected = True
                break
        
        if not connected:
            return False
            
    return True

def get_auth(active_chakras,active_channels_dict): 
    ''' 
        get authority from active chakras, 
        selection rules see #https://www.mondsteinsee.de/autoritaeten-des-human-design/
        Args:
            Chakras(set): active chakras
            active_channels_dict(dict): all active channels, keys: ["label","planets","gate","ch_gate"]
        Return:
            authority(str): return inner authority (SP,SL,SN,HT,GC,HT_GC,outher auth)
                HT_GC is reffered to ego projected
    '''
    outher_auth_mask = (("HD" in active_chakras) 
                        | ("AA" in active_chakras) 
                        | ("TT" in active_chakras)
                        | (len(active_chakras)==0)
                       )
    if "SP" in active_chakras:
        auth = "SP"
    elif "SL" in active_chakras:
        auth = "SL"
    elif "SN" in active_chakras:
        auth = "SN"
    elif (is_connected(active_channels_dict,"HT","TT")): #("HT" in active_chakras) &
        auth= "HT"
    elif (is_connected(active_channels_dict,"GC","TT")): #("GC" in active_chakras) &
        auth = "GC"
    elif ("GC" in active_chakras) & ("HT" in active_chakras):
        auth = "HT_GC"
    elif outher_auth_mask:
        auth = "outher_auth"
    else: auth = "unknown?" #sanity check;-)
    
    return auth
def get_typ(active_channels_dict, active_chakras): 
    ''' 
    get Energy-Type from active channels 
    Args:
        active_channels_dict(dict): all active channels, keys: ["label","planets","gate","ch_gate"]
        active_chakras(list/set): list of defined centers (e.g. ["SL", "RT", "GC"...])
    Return: 
        typ(str): typ (GENERATOR, MANIFESTING GENERATOR, PROJECTOR, MANIFESTOR, REFLECTOR)
    '''

    # --- 1. CHECK ROOT (RT) TO THROAT (TT) ---
    # Checks path: Throat -> Spleen -> Root OR Throat -> G-Center -> Spleen -> Root
    RT_TT_isconnected = (
        is_connected(active_channels_dict, "TT", "SN", "RT")
        | is_connected(active_channels_dict, "TT", "GC", "SN", "RT")
    )

    # --- 2. CHECK HEART (HT) TO THROAT (TT) ---
    # Checks path: Direct (21-45), Via G-Center, or Via Spleen
    TT_HT_isconnected = (
        is_connected(active_channels_dict, "TT", "HT")               # Direct (e.g., 21-45)
        | is_connected(active_channels_dict, "TT", "GC", "HT")       # Via G-Center
        | is_connected(active_channels_dict, "TT", "SN", "HT")       # Via Spleen
    )

    # --- 3. CHECK SACRAL (SL) TO THROAT (TT) ---
    # [FIX APPLIED HERE]
    # Previous code only checked via G-Center ("TT","GC","SL").
    # We now add the direct check ("TT","SL") for channel 20-34.
    TT_SL_isconnected = (
        is_connected(active_channels_dict, "TT", "GC", "SL")         # Via G-Center
        | is_connected(active_channels_dict, "TT", "SL")             # Direct (Channel 20-34)
    )

    # --- 4. CHECK ANY MOTOR TO THROAT ---
    # Combines all motor connections (Heart, Sacral, Solar Plexus, Root)
    # Note: Solar Plexus (SP) check is added directly here.
    TT_connects_SP_SL_HT_RT = (
        TT_HT_isconnected 
        | TT_SL_isconnected 
        | is_connected(active_channels_dict, "TT", "SP")             # Solar Plexus (e.g., 12-22, 35-36)
        | RT_TT_isconnected
    )

    # --- 5. DETERMINE TYPE ---
    
    # Rule 1: No Definition = Reflector
    if not len(active_chakras): 
        typ = "Reflector"      
    
    # Rule 2: Defined Sacral = Generator Family
    elif "SL" in active_chakras:
        if TT_connects_SP_SL_HT_RT:
            typ = "Manifesting Generator"
        else:
            typ = "Generator"
            
    # Rule 3: Undefined Sacral = Projector or Manifestor
    else: # (SL is NOT defined)
        if TT_connects_SP_SL_HT_RT:
            typ = "Manifestor"
        else:
            typ = "Projector"
            
    return typ


def get_component(active_channels_dict, chakra):
    """
    Helper function to get the component of a chakra in active channels.
    Args:
        active_channels_dict (dict): dictionary containing channel connections.
        chakra (str): the chakra label to check.
    Return:
        str: component identifier.
    """
    return active_channels_dict.get(chakra, None)



def get_channels_and_active_chakras(date_to_gate_dict,meaning=False):    
    ''' 
    calc active channels:
    take output of hd_features class (date_to_gate_dict) map each gate in col "gate" 
    to an existing channel gate in col "ch_gate" if channel exists, else value=0     
        dict for mapping: full_dict (all possible channels compinations)
    Args:
        date_to_gate_dict(dict):output of hd_feature class 
                                keys->[planets,label,longitude,gate,line,color,tone,base]
    Return:
        active_channels_dict(dict): all active channels, keys: ["label","planets","gate","ch_gate"]
        active_chakras(set): active chakras
    '''
    df = date_to_gate_dict
    #init lists
    gate_list =  df["gate"]
    ch_gate_list=[0]*len(df["gate"])
    active_chakras = []
    active_channels_dict={}
    gate_label_list=[]
    ch_gate_label_list=[]
    
    #map channel gates to gates, if channel exists and make list of it
    for idx,gate in enumerate(gate_list):

        ch_gate_a = full_dict["full_gate_1_list"]
        ch_gate_b = full_dict["full_gate_2_list"]
        gate_index=np.where(
            np.array(ch_gate_a)==gate
        )
        ch_gate = [ch_gate_b[index] 
                   for index in gate_index[0] 
                   if ch_gate_b[index] in gate_list
                  ]      
        if ch_gate:
            ch_gate_list[idx] = ch_gate[0] 
            active_chakras.append(
                full_dict["full_chakra_1_list"]
                [full_dict["full_gate_1_list"].index(gate)]
            )
            active_chakras.append(
                full_dict["full_chakra_2_list"]
                [full_dict["full_gate_2_list"].index(gate)]
            ) 
    df["ch_gate"]=ch_gate_list

    #filter dict for active channels (ch_gate is not 0)
    mask=np.array(df["ch_gate"])!=0
    
    #duplicate mask remove duplicates (e.g. (1,2) = (2,1))
    sorted_channels = [sorted((df["gate"][i],df["ch_gate"][i])) 
                       for i in range(len(df["gate"]))]
    unique_mask = np.unique(sorted_channels,axis=0,return_index=True)[1]
    dupl_mask = np.zeros(len(sorted_channels),dtype=bool)
    dupl_mask[unique_mask]=True
           
    #filter usefull keys to result dict
    for key in ["label","planets","gate","ch_gate"]: 
        active_channels_dict[key] = np.array(df[key])[dupl_mask&mask]   
    #map chakras to gates in new col["XXX_chakra"]
    active_channels_dict["gate_chakra"] =  [full_dict["full_gate_chakra_dict"][key] 
                                            for key in active_channels_dict["gate"]]
    active_channels_dict["ch_gate_chakra"] =  [full_dict["full_gate_chakra_dict"][key] 
                                               for key in active_channels_dict["ch_gate"]]
    #map labels to open gates and ch_gates
    gate=active_channels_dict["gate"]
    ch_gate=active_channels_dict["ch_gate"]
    
    # convert gates and channel gates to tuple format (1,2)
    for gate,ch_gate in zip(gate,ch_gate):
        idx_gate = np.where(
            np.array(df['gate'])==gate
        )
        idx_ch_gate = np.where(
            np.array(df['gate'])==ch_gate
        )
        gate_label_list.append(
            [df["label"][int(i)] for i in np.nditer(idx_gate)]
        )
        ch_gate_label_list.append(
            [df["label"][int(i)] for i in np.nditer(idx_ch_gate)]
        )
    active_channels_dict["ch_gate_label"] = ch_gate_label_list
    active_channels_dict["gate_label"] = gate_label_list
    
    #if meaning shall be mapped to active channels and returned
    if meaning:      
        #make dict searchable, normal and reversed channels are needed (eg. (1,2) == (2,1))
        meaning_dict = hd_constants.CHANNEL_MEANING_DICT
        full_meaning_dict = {**meaning_dict,**{key[::-1]:value
                                               for key,value in meaning_dict.items()}}
        #get channels in tuple  format
        channels =np.column_stack(
            (active_channels_dict["gate"],active_channels_dict["ch_gate"])
        ) 
        active_channels_dict["meaning"] = [full_meaning_dict[tuple(channel)] 
                                           for channel in channels] 

    return active_channels_dict,set(active_chakras)

def get_definition(active_channels_dict, active_chakras):
    """
    Calculates the number of continuous energy islands (connected components).
    
    Returns:
        0: No Definition (Reflector)
        1: Single Definition (Any topology: linear or cyclic)
        2: Split Definition
        3: Triple Split
        4: Quadruple Split
    """
    # 1. Handle Reflector (No defined centers)
    if not active_chakras:
        return 0

    # 2. Build Adjacency List (Map of connections)
    # Graph structure: { 'Sacral': {'Root', 'G_Center'}, ... }
    graph = {chakra: set() for chakra in active_chakras}
    
    gates = active_channels_dict["gate_chakra"]
    ch_gates = active_channels_dict["ch_gate_chakra"]
    
    for c1, c2 in zip(gates, ch_gates):
        if c1 in graph and c2 in graph:
            graph[c1].add(c2)
            graph[c2].add(c1)

    # 3. Count Connected Components (Islands)
    visited = set()
    islands = 0

    for chakra in active_chakras:
        if chakra not in visited:
            # Found a new island, start exploring it
            islands += 1
            stack = [chakra]
            visited.add(chakra)
            
            # Traverse the entire island
            while stack:
                node = stack.pop()
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)
                        
    return islands
    
def calc_full_gates_chakra_dict(gates_chakra_dict):
    ''' 
    from GATES_CHAKRA_DICT add keys in reversed order ([1,2]==[1,2]) 
    Args:
        gates_chakra_dict(dict): Constants are stored in hd_constants format {(64,47):("HD","AA"),...}
    Return:
        full_dict(dict): dict keys: full_ch_chakra_list,full_ch_list,full_ch_gates_chakra_dict,
                                    full_chakra_1_list,full_chakra_2_list,full_gate_1_list,
                                    full_gate_2_list,full_gate_chakra_dict
    '''
    cols = ["full_ch_chakra_list", #Chakra & Ch_Chakra of all 36*2(with reversed order e.g.["TT","AA"]&["AA","TT"]) channels
             "full_ch_list",       #all 36*2(with reversed order e.g.[1,2]&[2,1]) channels
             "full_ch_gates_chakra_dict", #dict channels:chakra of 36*2(with reversed order e.g.[1,2]&[2,1]) combinations
             "full_chakra_1_list",       #col 1 of full_chakra_list
             "full_chakra_2_list",       #col 2 of full_chakra_list 
             "full_gate_1_list",         #col 1 of full_ch_list
             "full_gate_2_list",         #col 2 of full_ch_list
             "full_gate_chakra_dict",    #dict gate:chakra, map gate to chakra
               ]       
    #init dict            
    full_dict = {k: [] for k in cols}

    #channels in normal and reversed order
    full_dict["full_ch_chakra_list"] = list(gates_chakra_dict.values()) + [item[::-1] 
                                                                           for item in gates_chakra_dict.values()]  
    #channel_chakras in normal and reversed order
    full_dict["full_ch_list"] = list(gates_chakra_dict.keys()) + [item[::-1] 
                                                                  for item in gates_chakra_dict.keys()]  
    #make dict from channels and channel chakras e.g. (1,2):("XX","YY")
    full_dict["full_ch_gates_chakra_dict"] = dict(
        zip(full_dict["full_ch_list"],
            full_dict["full_ch_chakra_list"])
    )
    #select each first chakra, len 72 
    full_dict["full_chakra_1_list"] = [item[0] 
                                       for item in full_dict["full_ch_chakra_list"]] 
    #select each second chakra, len 72
    full_dict["full_chakra_2_list"] = [item[1] 
                                       for item in full_dict["full_ch_chakra_list"]]  
    #select each first gate, len 72
    full_dict["full_gate_1_list"] = [item[0] 
                                     for item in full_dict["full_ch_list"]]  
    #select each second gate(channel_gate), len 72
    full_dict["full_gate_2_list"] = [item[1] 
                                     for item in full_dict["full_ch_list"]]  
    #make dict from first gate and first chakra list, len 72
    full_dict["full_gate_chakra_dict"] = dict(
        zip(full_dict["full_gate_1_list"],
            full_dict["full_chakra_1_list"])
    ) 
    
    return full_dict

#from chakra dict create full_dict (add keys in reversed order) 
full_dict = calc_full_gates_chakra_dict(hd_constants.GATES_CHAKRA_DICT)

def calc_full_channel_meaning_dict():
    """from meaning dict create full dict (add keys in reversed ordere.g. (1,2)/(2,1))"""
    meaning_dict = hd_constants.CHANNEL_MEANING_DICT
    full_meaning_dict = {**meaning_dict,**{key[::-1]:value for key,value in meaning_dict.items()}}
    return full_meaning_dict


def chakra_connection_list(chakra_1,chakra_2):
    ''' 
    from given chakras calc all posible connections (channels)
    list is enlarged by elements in reversed order (e.g. [1,2],[2,1])
    Args:
        chakra_1(str): start chakra 
        chakra_2(str): connecting chakra
    Return: 
        connection list(list): array of lists(gate:ch_gates)
    '''
    #create chakra_dict mask from given chakra and apply it to channel_list
    mask = ((np.array(full_dict["full_chakra_1_list"]) == chakra_1) 
            & (np.array(full_dict["full_chakra_2_list"]) == chakra_2)
           )
    connection_list = np.array(full_dict["full_ch_list"])[mask]
    #if list is not empty
    if len(connection_list): 
        full_connection_list = np.concatenate([connection_list, [item[::-1] 
                                                                 for item in connection_list]])# normal + reverse order   
    else: full_connection_list=[]
           
    return full_connection_list

def get_full_chakra_connect_dict():
    ''' get connecting channels between all possible chakras pairs 
        Return:
            connection_dict(dict):array of lists(gate:ch_gates)
    '''
    chakra_connect_dict = {}
    #all posible Chakra pairs of two
    for combination in itertools.combinations(hd_constants.CHAKRA_LIST, 2): 
        connect_channels = chakra_connection_list(*combination)
        chakra_connect_dict.update({combination:connect_channels})
               
    return chakra_connect_dict
        
