import hd_constants
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

def get_utc_offset_from_tz(timestamp,zone):
    """
    get utc offset from given time_zone. 
    DST (daylightsavingtime) is respectet (data from pytz lib)
    Args:
        zone(str): e.g. "Europe/Berlin"
    Return:
        hours(float): offset hours (decimal hours e.g. 0.75 for 45 min)
    """
    country = timezone(zone)
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    tz_offset = country.localize(datetime(*timestamp)).utcoffset().total_seconds()
    hours = tz_offset/3600
    return hours

class hd_features:
    ''' 
    class for calculation of basic human design features based on 
    given time_stamp (year,month,day,hour,minute,second,timezone_offset)
    
    basic hd_features:
                    date_to_gate_dict [planets,longitude,gate,line,color,tone,base]
                    profile,
                    inner authority,
                    typ(G=Generator,MG=Manifesting,Generator,P=Projector,
                        M=Manifestor,R=Reflector)
                    incranation cross,
                    active chakras,
                    active channels,
                    split
    extendet hd_features:
                    composition charts
                    penta analysis
   
    shortcuts used:
        Head Chakra = HD
        Anja Chakra = AA
        Throat Chakra = TT
        G-Centre = GC
        Hearth Chakra = HT
        Spleen Chakra = SN
        Solar Plexus Chakra = SP
        Sakral Chakra = SL
        Root Chakra = RT     
    '''    
    def __init__(self,year,month,day,hour,minute,second,tz_offset):
    
        '''
        Initialization of timestamp attributes for basic calculation 
        hd_constants.py 
        '''
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.tz_offset = tz_offset
        self.time_stamp = year,month,day,hour,minute,second,tz_offset
        
        '''
        Constant values are stored in hd_constants.py
            SWE_PLANET_DICT:
                calculation is based on swiss epheremis lib #https://github.com/astrorigin/pyswisseph
                    each planet is represented by a number
            IGING_CIRCLE
                order of gates in rave chart
            CHAKRA_LIST 
                list of all chakras, appreveation see above
        '''
        self.SWE_PLANET_DICT = hd_constants.SWE_PLANET_DICT 
        self.IGING_CIRCLE_LIST = hd_constants.IGING_CIRCLE_LIST 
        self.CHAKRA_LIST = hd_constants.CHAKRA_LIST
 
    def timestamp_to_juldate(self,*time_stamp):
        ''' 
        calculate julian date from given timestamp:
            -uses swiss_ephemeris lib  www.astro.com #astrodienst
            -if historic daylight time saving data is unknown may see below:
                https://www.ietf.org/timezones/tzdb-2018f/tz-link.html
        Args: 
            self, timestamp(tuple): format: year,month,day,hour,minute,second,time_zone_offeset
        Return: 
            julian date(float)
        '''
        time_zone = swe.utc_time_zone(*self.time_stamp)
        jdut = swe.utc_to_jd(*time_zone)

        return jdut[1]
    
    def calc_create_date(self,jdut):
        ''' 
        calculate creation date from birth data:
            #->sun position -88° long, aprox. 3 months before (#source -> Ra Uru BlackBook)
        For calculation swiss_ephemeris lib is used 
        Args: 
           julian date(float): timestamp in julian day format
        Return: 
            creation date (float): timestamp in julian day format
        '''
        design_pos = 88 
        sun_long =  swe.calc_ut(jdut, swe.SUN)[0][0]
        long = swe.degnorm(sun_long - design_pos) 
        tstart = jdut - 100 #aproximation is start -100°
        res = swe.solcross_ut(long, tstart)
        create_date = swe.revjul(res)
        create_julday = swe.julday(*create_date)
        
        return create_julday
    
    def date_to_gate(self,jdut,label):
        '''
        from planetary position (longitude) basic hd_features are calculated:
            features: 
                planets,longitude,gates lines, colors, tone base
        
        uses swiss_ephemeris lib www.astro.com #astrodienst for calculation
        Args:
            julian day(float): timestamp in julian day format
            label(str): indexing for create and birth values
        Return:
            value_dict (dict)
        '''   
        
        """synchronize zodiac and gate-circle (IGING circle) = 58°""" 
        offset= hd_constants.IGING_offset

        result_dict = {k: [] 
                       for k in ["label",
                                 "planets",
                                 "lon",
                                 "gate",
                                 "line",
                                 "color",
                                 "tone",
                                 "base"]
                      }

        for idx,(planet,planet_code) in enumerate(self.SWE_PLANET_DICT.items()):
            xx = swe.calc_ut(jdut,planet_code)
            long = xx[0][0]
            
            #sun position is base of earth position
            if planet =="Earth": 
                long = (long+180) % 360 #Earth is in opp. pos., angles max 360°

            #north node is base for south node position
            elif planet == "South_Node":
                long = (long+180) % 360 #North Node is in opp. pos.,angles max 360°
                
            angle = (long + offset) % 360 #angles max 360°
            angle_percentage =angle/360 
            
            #convert angle to gate,line,color,tone,base
            gate = self.IGING_CIRCLE_LIST[int(angle_percentage*64)] 
            line = int((angle_percentage*64*6)%6+1)
            color =int((angle_percentage*64*6*6)%6+1)
            tone =int((angle_percentage*64*6*6*6)%6+1)
            base =int((angle_percentage*64*6*6*6*5)%5+1)

            result_dict["label"].append(label)
            result_dict["planets"].append(planet)
            result_dict["lon"].append(long)
            result_dict["gate"].append(gate)
            result_dict["line"].append(line)
            result_dict["color"].append(color)
            result_dict["tone"].append(tone)
            result_dict["base"].append(base)
            
        return result_dict

    def birth_creat_date_to_gate(self,*time_stamp):
        '''
        concatenate birth- and create date_to_gate_dict 
           Args:
                time_stamp(tuple): format(year,month,day,hour,minute,second,timezone_offset)
           Return: 
                date_to_gate_dict(dict): keys->[planets,label,longitude,gate,line,color,tone,base]
        '''
        birth_julday = self.timestamp_to_juldate(time_stamp)
        create_julday = self.calc_create_date(birth_julday)
        birth_planets = self.date_to_gate(birth_julday,"prs")
        create_planets = self.date_to_gate(create_julday,"des")
        date_to_gate_dict = {
            key: birth_planets[key] + create_planets[key] 
            for key in birth_planets.keys()
                            }
        self.date_to_gate_dict = date_to_gate_dict
        self.create_date = swe.jdut1_to_utc(create_julday)[:-1]
        
        return date_to_gate_dict
    
    def day_chart(self,*time_stamp):
        '''calculate day chart
           Args:
                time_stamp(tuple): format(year,month,day,hour,minute,second,timezone_offset)
           Return: 
                date_to_gate_dict(dict): keys->[planets,label,longitude,gate,line,color,tone,base] of daychart
        '''
        birth_julday = self.timestamp_to_juldate(time_stamp)
        birth_planets = self.date_to_gate(birth_julday,"prs")
        result_dict = birth_planets

        return result_dict
    
    
#############################################################################
"""calculation functions based on hd_features based-class starts from here"""

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

def is_connected(active_channels_dict,*args):
    ''' 
    get bool answer wheater chakras are connected through channel or not
    direct and indirekt connections are supported (e.g ["TT","AA"],["TT","SN","RT"))
        Params: 
           active_channels_dict(dict): all active channels, keys: ["label","planets","gate","ch_gate"]
           given_chakras(str): Chakras that will be checked                                    
    Return:
        bool: returns True if is connected, and false if not
    '''
    #if gate list is emtpy ->Reflector-Typ (no channels at all), return false
    if not len(active_channels_dict["gate"]):
        return False
    else:
        gate_chakra_mask = np.array(
            [gate_chakra in args 
             for gate_chakra in active_channels_dict["gate_chakra"]]
        ) 
        ch_gate_chakra_mask = np.array(
            [ch_gate_chakra in args for 
             ch_gate_chakra in active_channels_dict["ch_gate_chakra"]]
        )
        
        #if gate and channel gate in same line -> is connected
        mask = gate_chakra_mask & ch_gate_chakra_mask 
        
        #for 2 elements 1 connection, for 3 elements 2 connection, ...
        if sum(mask)>=len(args)-1: 
            return True
        else: return False

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
    get Energie-Type from active channels 
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
        typ = "REFLECTOR"      
    
    # Rule 2: Defined Sacral = Generator Family
    elif "SL" in active_chakras:
        if TT_connects_SP_SL_HT_RT:
            typ = "MANIFESTING GENERATOR"
        else:
            typ = "GENERATOR"
            
    # Rule 3: Undefined Sacral = Projector or Manifestor
    else: # (SL is NOT defined)
        if TT_connects_SP_SL_HT_RT:
            typ = "MANIFESTOR"
        else:
            typ = "PROJECTOR"
            
    return typ

def get_typ_old1(active_channels_dict,active_chakras): 
    ''' 
    get Energie-Type from active channels 
        selection rules see (ref.: https://www.mondsteinsee.de/human-design-typen/)
    Args:
        active_channels_dict(dict): all active channels, keys: ["label","planets","gate","ch_gate"]
    Return: 
        typ(str): typ (G=Generator,MG=Manifesting,Generator,P=Projector,
                       M=Manifestor,R=Reflector)
    '''
    #print (active_channels_dict)
    #root is connected with throat? (direct,indirect)
    RT_TT_isconnected = (is_connected(active_channels_dict,"TT","SN","RT")
                         |is_connected(active_channels_dict,"TT","GC","SN","RT")
                        )
    #throat is connected with hearth? (direct,indirect)                   
    TT_HT_isconnected = (is_connected(active_channels_dict,"TT","HT")
                         | is_connected(active_channels_dict,"TT","GC","HT")
                         | is_connected(active_channels_dict,"TT","SN","HT")
                        )
    #throat is connected with sakral centre? (indirect)
    TT_SL_isconnected = is_connected(active_channels_dict,"TT","GC","SL")
    #is throat connected with energy centres (SP,SL,HT,RT)?
    TT_connects_SP_SL_HT_RT = (TT_HT_isconnected 
                               | TT_SL_isconnected 
                               | is_connected(active_channels_dict,"TT","SP") 
                               | RT_TT_isconnected
                              )

    #if list is empty -> R-Typ
    if  not len(active_chakras): 
        typ ="REFLECTOR"      
    elif ("SL" in active_chakras) & (TT_connects_SP_SL_HT_RT==False):
        typ = "GENERATOR"
    elif ("SL" in active_chakras) & (TT_connects_SP_SL_HT_RT):
        typ = "MANIFESTING GENERATOR"   
    elif ("SL" not in active_chakras) & (TT_connects_SP_SL_HT_RT==False):
        typ = "PROJECTOR"   
    elif ("SL" not in active_chakras) & (TT_connects_SP_SL_HT_RT):
        typ = "MANIFESTOR"

    return typ

def get_typ_old(active_channels_dict, active_chakras):
    ''' 
    Get Energy-Type from active channels.
    Args:
        active_channels_dict (dict): all active channels, keys: ["label", "planets", "gate", "ch_gate"]
        active_chakras (list): all active centers (chakras)
    Return: 
        typ (str): Type (GENERATOR, MANIFESTING GENERATOR, PROJECTOR, MANIFESTOR, REFLECTOR)
    '''
    
    # No active centers => Reflector
    if len(active_chakras) == 0:
        return "REFLECTOR"
    
    # Case: Sacral is undefined (can be Manifestor or Projector)
    if "SL" not in active_chakras:
        # If Throat is undefined, it must be a Projector
        if "TT" not in active_chakras:
            return "PROJECTOR"

        # Check connections from motor centers (HT, EM, RT) to throat (=> Manifestor)
        component = get_component(active_channels_dict, "TT")  # Throat component
        if "HT" in active_chakras and get_component(active_channels_dict, "HT") == component:
            return "MANIFESTOR"
        if "EM" in active_chakras and get_component(active_channels_dict, "EM") == component:
            return "MANIFESTOR"
        if "RT" in active_chakras and get_component(active_channels_dict, "RT") == component:
            return "MANIFESTOR"
        
        # If no motor center is connected to the throat, it is a Projector by definition
        return "PROJECTOR"
    
    # Case: Sacral is defined (can be Generator or Manifesting Generator)
    if "TT" not in active_chakras:
        return "GENERATOR"

    # Check connections from motor centers (HT, EM, RT) to throat (=> Manifesting Generator)
    if "HT" in active_chakras and get_component(active_channels_dict, "HT") == get_component(active_channels_dict, "TT"):
        return "MANIFESTING GENERATOR"
    if "EM" in active_chakras and get_component(active_channels_dict, "EM") == get_component(active_channels_dict, "TT"):
        return "MANIFESTING GENERATOR"
    if "RT" in active_chakras and get_component(active_channels_dict, "RT") == get_component(active_channels_dict, "TT"):
        return "MANIFESTING GENERATOR"
    if get_component(active_channels_dict, "SL") == get_component(active_channels_dict, "TT"):
        return "MANIFESTING GENERATOR"

    # No connection to throat => Generator
    return "GENERATOR"

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

def get_split(active_channels_dict,active_chakras):
    """
    calculate split from active channels and chakras
    if 
        connection is circular -> no split -> return:0
        connection is bicircular-> no split -> return:-1
        all chakras are linear connected-> no split ->return:1
        two connected groups-> split -> return:2,
        three connect groups ....
    Args:
        active_channels_dict(dict): all active channels, keys: ["label","planets","gate","ch_gate"]
        active_chakras(set): active chakras
    Return:
        split(int): meaning see above
    """
    #split, remove duplicate tuples (gate,ch_gate chakras) in channels 
    gate_chakra = active_channels_dict["gate_chakra"]
    ch_gate_chakra = active_channels_dict["ch_gate_chakra"]
    sorted_chakras = [sorted((gate_chakra[i],ch_gate_chakra[i])) 
                      for i in range(len(active_channels_dict["gate_chakra"]))]
    unique_mask = np.unique(sorted_chakras,axis=0,return_index=True)[1]
    dupl_mask = np.zeros(len(sorted_chakras),dtype=bool)
    dupl_mask[unique_mask]=True
    len_no_dupl_channel = sum(dupl_mask)
    split = len(active_chakras) - len_no_dupl_channel
    
    return  split
    
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
        
def calc_single_hd_features(timestamp,report=False,channel_meaning=False,day_chart_only=False):
    '''
    from given timestamp calc basic additional hd_features
    print report if requested
    use hd_features base class
    Params: 
        timestamp (tuple): (year,month,day,hour,minute,second,tz_offset),                                          
        report (bool): prints text Report of key features, used for single timestamp calc.
        channel_meaning: add meaning to channels
       Return: 
            gate (int), #selected col of planet_df
            active_chakra(set): all active chakras
            typ(str): energy typ [G,MG,P,M,R]
            authority(str): [SP,SL,SN,HT,GC,outher auth]
            incarnation cross(tuple): format ((1,2),(3,4))
            profile(tuple): format (1,2)
            active_channels(dict):  keys [planets,labels,gates and channel gates]
    '''
    ####santity check for input format and values
    if ((len(timestamp)!=7)
    | (len([elem for elem in timestamp[1:6] if elem <0]))
    | (timestamp[1]>12) 
    | (timestamp[2]>31) 
    | (timestamp[3]>24) 
    | (timestamp[4]>60) 
    | (timestamp[5]>60)
        ):
        sys.stdout.write("Format should be:\
        Year,Month,day,hour,min,sec,timezone_offset,\nIs date correct?")
        raise ValueError('check timestamp Format') 
    else:
        instance = hd_features(*timestamp) #create instance of hd_features class

        if day_chart_only:
            date_to_gate_dict = instance.day_chart(instance.time_stamp)
        else:
            date_to_gate_dict = instance.birth_creat_date_to_gate(instance.time_stamp) 
            active_channels_dict,active_chakras = get_channels_and_active_chakras(
                date_to_gate_dict,meaning=channel_meaning)
            typ = get_typ(active_channels_dict,active_chakras)
            auth = get_auth(active_chakras,active_channels_dict)
            inc_cross = get_inc_cross(date_to_gate_dict)
            inc_cross_typ = inc_cross[-3:]
            profile = get_profile(date_to_gate_dict)
            split = get_split(active_channels_dict,active_chakras)
            variables = get_variables(date_to_gate_dict)
            bdate="{}".format(timestamp[:-2])
            cdate="{}".format(instance.create_date)
            if report == True:
#                print("birth date: {}".format(timestamp[:-2]))
                print("birth date: "+ bdate)
#                print("create date: {}".format(instance.create_date))
                print("create date: " + cdate)
                print("energie-type: {}".format(typ))
                print("inner authority: {}".format(auth))
                print("inc. cross: {}".format(inc_cross))
                #print("profile: {}".format(profile))
                print("profile: {}/{}".format( *profile, sep='/'))
                print("active chakras: {}".format(active_chakras))
                print("split: {}".format(split))
                print("variables: {}".format(variables))
                display(pd.DataFrame(date_to_gate_dict))
                display(pd.DataFrame(active_channels_dict))
         
    if day_chart_only==False:
        return  typ,auth,inc_cross,inc_cross_typ,profile,split,date_to_gate_dict,active_chakras,active_channels_dict, bdate, cdate
    else:
        return date_to_gate_dict

def unpack_single_features(single_result):
    '''
    convert tuple format into dict
    Args:
        single_result(tuple(lists)): hd_key features
    Return:
        return_dict(dict): keys: "typ","auth","inc_cross","profile"
                                 "split,"date_to_gate_dict","active_chakra"
                                 "active_channel"
    '''
    return_dict = {}
    # unpacking multiple calculation values
    return_dict["typ"] = single_result[0]
    return_dict["auth"] = single_result[1] 
    return_dict["inc_cross"] = single_result[2]
    return_dict["inc_cross_typ"] = single_result[3]
    return_dict["profile"] = single_result[4]
    return_dict["split"] = single_result[5]
    return_dict["date_to_gate_dict"] = single_result[6]
    return_dict["active_chakra"] = single_result[7]
    return_dict["active_channel"] = single_result[8]
    return_dict["birth_date"] = single_result[9]
    return_dict["create_date"] = single_result[10]
    
    return return_dict

def get_timestamp_list(start_date,end_date,percentage,time_unit,intervall): 
    ''' 
    make list of timestamps (format: year,month,day,hour,minute) 
        in given time range (start->end)
        seconds, and tz_offset will be automatic zero
    Args:
        start_date(tuple): (year,month,day,hour,minute,second,timezone_offset)
        end_date(tuple): (year,month,day,hour,minute,second,timezone_offset)
        percentage(float): how much % of list is processed (e.g. for trial runs)
        time_unit (str): = years,months,days,hours,minutes can be used
        intervall (int) = stepwith, count every X unit(years,months,days,hours,minutes are supported)
    Return: 
        list of tuple: format: year,month,day,hour,minute,second,tz_offset
    
    Examples : get_timestamp_list((2000,12,31,23,57),(2000,12,31,23,59),1,"minutes",1)
               -> [(2000,12,31,23,59,0,0),(2000,12,31,23,58,0,0)]           
    Note: 
       Precision for hd_calculations
           every gate changes in 5.71 days, 136.97 hours, 8218.12 minutes
           every line changes in 0.95 days, 22.83 hours, 1369.69 minutes
           every color changes in 0.16 days, 3.80 hours, 228.28 minutes
           every tone changes in 0.03 days, 0.63 hours, 38.05 minutes
           every base changes in 0.01 days, 0.13 hours, 7.61 minutes
    '''
    start_date = datetime(*start_date)
    end_date = datetime(*end_date)

    if  time_unit =="years":
        unit=60*60*24*365.2425
    elif time_unit =="months":
        unit=60*60*24*365.25/12
    if time_unit =="days":
        unit=60*60*24 
    elif time_unit =="hours":
        unit=60*60 
    elif time_unit =="minutes":
        unit=60
        
    time_diff_range = int((end_date-start_date).total_seconds()/(unit)) 
    timestamp_list = []
    for idx,i in enumerate(range(int(time_diff_range*percentage/intervall))):
        #relativdelta native supports year,month
        if (time_unit == "years") | (time_unit == "months"):
            new_date = end_date-i*relativedelta(**{time_unit: intervall})
        #timedelta is faster
        else:
            new_date = end_date-i*timedelta(**{"seconds": unit*intervall})
            
        timestamp = new_date.year,new_date.month,new_date.day,new_date.hour,new_date.minute,0,0
        timestamp_list.append(timestamp)

    #sanity check, if date range or intervall makes sense    
    if not len(timestamp_list):
        raise ValueError('check startdate < enddate & (enddate-intervall) >= startdate')  
    return timestamp_list
    
def calc_mult_hd_features(start_date,end_date,percentage,time_unit,intervall,num_cpu):
    """
    calculate multiple hd_features from given timerange
    Args:
        start_date(tuple): year,month,day,hour,minute,second,tz_offset
        end_date(tuple): year,month,day,hour,minute,second,tz_offset (end>start)
        percentage(float): percentage of given time range
        unit(str): years,months,days,hours,minutes
        intervall(int): stepwith, every X unit
        num_cpu(int): for multiprocessing
    Return: 
        result(list): hd_features(typ,auth,inc,profile,gate_dict,chakra,channel)
        timestamp_list(list): list of datetime timestamps
    """
    p = Pool(num_cpu)
    timestamp_list=get_timestamp_list(start_date,end_date,percentage,time_unit,intervall) #line change every 22 hour
    result = process_map(calc_single_hd_features,timestamp_list,chunksize=num_cpu)
    p.close()
    p.join()
    
    return result,timestamp_list

def unpack_mult_features(result,full=True):
    '''
    convert nested lists into dict
    if full: date_to_gate list is also extracted to new dict 
    Args:
        result(list): result from multi timestamp calculation (nested lists)
    Return:
        return_dict(dict): keys: "typ","auth","inc_cross","profile"
                                 "split,"date_to_gate_dict","active_chakra"
                                 "active_channel"
    '''
    return_dict = {}
    # unpacking multiple calculation values
    return_dict["typ_list"] = [result[i][0] for i in range (len(result))]
    return_dict["auth_list"] = [result[i][1] for i in range (len(result))]
    return_dict["inc_cross_list"] = [result[i][2] for i in range (len(result))]
    return_dict["inc_cross_typ_list"] = [result[i][3] for i in range (len(result))]
    return_dict["profile_list"] = [result[i][4] for i in range (len(result))]
    return_dict["split_list"] = [result[i][5] for i in range (len(result))]
    return_dict["date_to_gate_dict"] = [result[i][6] for i in range (len(result))]
    return_dict["active_chakra_list"] = [result[i][7] for i in range (len(result))]
    return_dict["active_channel_list"] = [result[i][8] for i in range (len(result))]
    
    if full:
        #extract date_to_gate_dict lists value keys'lon', 'gate', 'line', 'color', 'tone', 'base'
        return_dict["gate_list"] = [return_dict["date_to_gate_dict"][i]["gate"] 
                                    for i in range(len(return_dict["date_to_gate_dict"]))]
        return_dict["line_list"] = [return_dict["date_to_gate_dict"][i]["line"] 
                                    for i in range(len(return_dict["date_to_gate_dict"]))]
        return_dict["lon_list"] = line_list = [return_dict["date_to_gate_dict"][i]["lon"] 
                                    for i in range (len(return_dict["date_to_gate_dict"]))]
        return_dict["color_list"] = [return_dict["date_to_gate_dict"][i]["color"] 
                                    for i in range (len(return_dict["date_to_gate_dict"]))]
        return_dict["tone_list"] = [return_dict["date_to_gate_dict"][i]["tone"] 
                                    for i in range (len(return_dict["date_to_gate_dict"]))]
        return_dict["base_list"] = [return_dict["date_to_gate_dict"][i]["base"] 
                                    for i in range (len(return_dict["date_to_gate_dict"]))]
      
    return return_dict
    
def get_single_hd_features(persons_dict,key,feature):
    """
    get hd features of specified person and unpack values for composite charts proc.
    Args: 
        person dict(dict): eg {"person1":(2022,2,2,2,22,0,2),"person2":(1922,2,2,2,22,0,2)}
        key (str): e.g. "person1"
        feature(str): "date_to_gate_dict"
    Return
        feature_values(dict) of person
    """
    single_result = calc_single_hd_features(persons_dict[key],report=False)
    
    return unpack_single_features(single_result)[feature]

def composite_chakras_channels(persons_dict,identity,other_person):
    """
    get composite chakras and channels of two identities
    uses pd.DataFrames format, therefore might be slower
    Args:
        person dict(dict): eg {"person1":(2022,2,2,2,22,0,2),"person2":(1922,2,2,2,22,0,2)}
        identity: person1 (in person dict)
        other person: person2 (in person dict)
    Return
        new_channels(pd.DFrame): new channel of composite chart
        duplicated_channels(od.DataFrame):channels that are present oin both persons
        new_chakras(set): new chakras that are activated by connecting gates of both persons
        composite_chakras(set): all chakras in new composite chart
    """
    #get hd_features of given persons
    other_gate_dict = get_single_hd_features(persons_dict,other_person,'date_to_gate_dict')
    identity_gate_dict = get_single_hd_features(persons_dict,identity,'date_to_gate_dict')
    #concat composite dict to new one
    for person in [identity,other_person]:
        composite_dict = {key:other_gate_dict[key] + identity_gate_dict[key] 
                          for key in other_gate_dict.keys()}    
    #get channels and chakra of identity, other and composite chart
    composite_channels_dict,composite_chakras = get_channels_and_active_chakras(composite_dict,meaning=True)
    id_channels_dict,id_chakras = get_channels_and_active_chakras(identity_gate_dict,meaning=True)
    other_channels_dict,other_chakras = get_channels_and_active_chakras(other_gate_dict,meaning=True)
    #convert to pd.dataframe
    composite_channels = pd.DataFrame(composite_channels_dict)
    id_channels = pd.DataFrame(id_channels_dict)
    other_channels = pd.DataFrame(other_channels_dict)
    #get new channels,chakras
    mask_new = composite_channels["meaning"].isin(
        pd.concat([id_channels["meaning"],other_channels["meaning"]]))
    mask_duplicated=id_channels["meaning"].isin(
        other_channels["meaning"])
    new_channels = composite_channels[~mask_new]
    duplicated_channels = id_channels[mask_duplicated]
    new_chakras = composite_chakras-id_chakras
    
    return new_channels,duplicated_channels,new_chakras,composite_chakras

def get_composite_combinations(persons_dict):
    ''' 
    get composite features of two persones in pd.dataframe format
    If more than two persons in dict, every combination is calculated
    Args:
        person dict(dict): eg {"person1":(2022,2,2,2,22,0,2),"person2":(1922,2,2,2,22,0,2)}
    Return:
        pd.Dataframe of composite features of every pair combination in persons dict
    '''
    result_dict = {"id":[],"other_person":[],"new_chakra":[],"chakra_count":[],"new_channels":[],"new_ch_meaning":[]}
    
    for idx,combination in enumerate(list(itertools.combinations(persons_dict.keys(),2))):

        identity = combination[0]
        other_person = combination[1]
        new_channels,dupl_channels,new_chakras,comp_chakras = composite_chakras_channels(
            persons_dict,identity,other_person)

        result_dict["id"] = result_dict["id"] + [identity]
        result_dict["other_person"] = result_dict["other_person"] + [other_person]
        result_dict["new_chakra"] = result_dict["new_chakra"] + [list(new_chakras)]
        result_dict["chakra_count"] = result_dict["chakra_count"] + [int(len(comp_chakras))]
        result_dict["new_channels"] = result_dict["new_channels"] + [list(zip(new_channels["gate"],new_channels["ch_gate"]))]
        result_dict["new_ch_meaning"] = result_dict["new_ch_meaning"] + [list(new_channels["meaning"])]

    result_df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in result_dict.items()]))
    
    return result_df

def get_penta(persons_dict,report=False):
    """
    take gates of given identity combination (concat) and look if it matches to "penta" gates
    Args:
         person dict(dict): eg {"person1":(2022,2,2,2,22,0,2),"person2":(1922,2,2,2,22,0,2)}
         report(bool): print full report (dataframe, with every gate matched)
    Return:
        df(pd.Dataframe): penta gates as cols
                          if identity combination has penta gate:x, else:0 
        persentage(float): how much percent of penta is matched
    """
    penta_dict = hd_constants.penta_dict
    
    for person in persons_dict.keys():
        identity_dict = get_single_hd_features(persons_dict,person,'date_to_gate_dict')
        person_gate_list=np.array(identity_dict["gate"])
        person_penta_gates = np.intersect1d(person_gate_list,np.array(list(penta_dict.keys())))

        for key in penta_dict.keys():
            if key in person_penta_gates:
                penta_dict[key]=[person] + penta_dict[key]

    result_dict = {elem:pd.Series(persons_dict.keys()).isin(penta_dict[elem]) 
                   for elem in penta_dict.keys()}
    penta_gates_bool = [(any(result_dict[key])) for key in result_dict.keys()]
    sum_penta_gates = sum(penta_gates_bool)
    if report:
        df = pd.DataFrame(result_dict) 
        df.loc[df.shape[0]+1,:] = [any(df[col]) for col in df.columns]
        df = df.replace({False:"o",True:"x"})
        df["index"] = list(persons_dict.keys())+["all"]
        df = df.set_index("index",drop=True)
        print(df)
    return round(sum_penta_gates/12*100,2)



class hd_composite:

    def __init__(self,birth_timestamp,start_date,end_date,percentage,time_unit,intervall,num_cpu):
    
        '''
        Initialization of timestamp attributes for basic calculation 
        hd_constants.py 
        '''
        self.birth_timestamp = birth_timestamp
        self.start_date = start_date
        self.end_date = end_date
        self.percentage = percentage
        self.time_unit = time_unit
        self.intervall = intervall
        self.num_cpu = num_cpu
    
    def date_to_gate_hd_chart(self):
        hd_chart_birth = calc_single_hd_features(self.birth_timestamp,
                                                report=False,channel_meaning=True,day_chart_only=False)
        date_to_gate_birth = hd_chart_birth[6] # only date_to_gate_dict
        del date_to_gate_birth["ch_gate"] #for concat both dicts

        self.date_to_gate_birth = date_to_gate_birth

        return date_to_gate_birth

    def get_composite_hd_day_chart(self,day_date):
        date_to_gate_day = calc_single_hd_features(
                                day_date,
                                day_chart_only=True)

        #concat day chart and birth chart to new identity
        date_to_gate_dict = {
                    key: self.date_to_gate_birth [key] + date_to_gate_day[key] 
                    for key in self.date_to_gate_birth.keys()
                                    }

        #get channels and chakras
        active_channels_dict,active_chakras = (get_channels_and_active_chakras(
                                                    date_to_gate_dict))
        typ = get_typ(active_channels_dict,active_chakras)
        auth = get_auth(active_chakras,active_channels_dict)
        split = get_split(active_channels_dict,active_chakras)
        planets = date_to_gate_dict
        return active_channels_dict,active_chakras,typ,auth,split,planets

    def calc_multi_comp_charts(self):
    
        timestamp_list=get_timestamp_list(
                                self.start_date,
                                self.end_date,
                                self.percentage,
                                self.time_unit,
                                self.intervall) #line change every 22 hour
        p = Pool(self.num_cpu)
        result = process_map(self.get_composite_hd_day_chart,timestamp_list,chunksize=self.num_cpu)
        p.close()
        p.join()

        self.result = result
        self.timestamp_list = timestamp_list

    def unpack_mult_features(self):
        '''
        convert nested lists into dict
        if full: date_to_gate list is also extracted to new dict 
        Args:
            result(list): result from multi timestamp calculation (nested lists)
        Return:
            return_dict(dict): keys: "typ","auth","inc_cross","profile"
                                    "split,"date_to_gate_dict","active_chakra"
                                    "active_channel"
        '''
        return_dict = {}
        # unpacking multiple calculation values

        return_dict["active_channel_list"] = [self.result[i][0] for i in range (len(self.result))]
        return_dict["active_chakra_list"] = [self.result[i][1] for i in range (len(self.result))]
        return_dict["typ_list"] = [self.result[i][2] for i in range (len(self.result))]
        return_dict["auth_list"] = [self.result[i][3] for i in range (len(self.result))]
        return_dict["split_list"] = [self.result[i][4] for i in range (len(self.result))]
        return_dict["planet_dict_list"] = [self.result[i][5] for i in range (len(self.result))]

        return return_dict
