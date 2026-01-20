from .. import hd_constants
import swisseph  as swe  
from IPython.display import display
import pandas as pd
import itertools
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pytz import timezone
from multiprocessing import Pool
from tqdm.contrib.concurrent import process_map
import sys
from .attributes import (
    get_inc_cross,
    get_profile,
    get_variables
)
from .mechanics import (
    get_channels_and_active_chakras,
    get_typ,
    get_auth,
    get_definition
)

def get_utc_offset_from_tz(timestamp,zone):
    """
    get utc offset from given time_zone. 
    dst (daylightsavingtime) is respected (data from pytz lib)
    Args:
        zone(str): e.g. "Europe/Berlin"
    Return:
        hours(float): offset hours (decimal hours e.g. 0.75 for 45 min)
    """
    country = timezone(zone)
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
                    Type(G=Generator,MG=Manifesting,Generator,P=Projector,
                        M=Manifestor,R=Reflector)
                    incarnation cross,
                    active chakras,
                    active channels,
                    definition
    extended hd_features:
                    composition charts
                    penta analysis
   
    shortcuts used:
        Head Chakra = HD
        Ajna Chakra = AA
        Throat Chakra = TT
        G-Centre = GC
        Heart Chakra = HT
        Spleen Chakra = SN
        Solar Plexus Chakra = SP
        Sacral Chakra = SL
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
    
    
    def calc_solar_return_jd(self, jdut, year_offset=0):
        '''
        Calculate the Julian date of the Solar Return for a specific year.
        Args:
           jdut (float): Julian date of birth.
           year_offset (int): Year offset from birth (0 for the current SR since birth).
        Return:
            sr_julian_day (float): Julian date of the Solar Return.
        '''
        # 1. Convert birth Julian Date back to UTC time components
        # Note: If year_offset is 0, swisseph finds the *next* return after the birth date.
        # If year_offset > 0, we estimate the JD start search to find the correct SR.
        
        # Determine the year to start the search from (beginning of the target SR year)
        # revjul returns (y, m, d, h_decimal)
        year, month, day, hour_decimal = swe.revjul(jdut)
        
        # Convert decimal hour to h, m, s for datetime
        hour = int(hour_decimal)
        minute_float = (hour_decimal - hour) * 60
        minute = int(minute_float)
        second = int((minute_float - minute) * 60)
        
        dt_start = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        
        target_year = dt_start.year + year_offset
        # Start search from the beginning of the target calendar year
        target_year_start_dt = datetime(target_year, 1, 1, 0, 0, 0)
        
        # Convert to decimal hour for swe.julday
        hour_dec = target_year_start_dt.hour + target_year_start_dt.minute/60.0 + target_year_start_dt.second/3600.0
        
        target_year_start_jd = swe.julday(
            target_year_start_dt.year, target_year_start_dt.month, target_year_start_dt.day, 
            hour_dec
        )

        # 3. Calculate Natal Sun Longitude
        # Use FLG_SWIEPH (default) or whatever flag is appropriate.
        # swe.SUN is 0
        natal_sun_res = swe.calc_ut(jdut, swe.SUN)
        natal_sun_lon = natal_sun_res[0][0]

        # 4. Use swe.solcross_ut to find when Sun returns to this longitude
        # It searches forward from target_year_start_jd
        sr_jdut = swe.solcross_ut(natal_sun_lon, target_year_start_jd)
        
        return sr_jdut

    def get_solar_return_date(self, year_offset):
        '''
        Calculates the UTC date and time of the Solar Return.
        '''
        birth_julday = self.timestamp_to_juldate(self.time_stamp)
        sr_julday = self.calc_solar_return_jd(birth_julday, year_offset)
        
        # swe.jdut1_to_utc returns (year, month, day, hour, minute, second)
        # We take all 6 values
        sr_utc_date_tuple = swe.jdut1_to_utc(sr_julday)
        # Round seconds to integer if needed, or keep as is.
        # Ensure we have 6 elements for API.
        if len(sr_utc_date_tuple) >= 6:
             sr_utc_date_tuple = sr_utc_date_tuple[:6]
        else:
             # Fallback if fewer elements
             sr_utc_date_tuple = tuple(list(sr_utc_date_tuple) + [0]*(6-len(sr_utc_date_tuple)))

        return sr_utc_date_tuple    

    
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
            definition = get_definition(active_channels_dict,active_chakras)
            variables = get_variables(date_to_gate_dict)
            bdate="{}".format(timestamp[:-2])
            cdate="{}".format(instance.create_date)
            if report:
                print("birth date: "+ bdate)
                print("create date: " + cdate)
                print("energy-type: {}".format(typ))
                print("inner authority: {}".format(auth))
                print("inc. cross: {}".format(inc_cross))
                print("profile: {}/{}".format( *profile, ))
                print("active chakras: {}".format(active_chakras))
                print("definition: {}".format(definition))
                print("variables: {}".format(variables))
                display(pd.DataFrame(date_to_gate_dict))
                display(pd.DataFrame(active_channels_dict))
         
    if not day_chart_only:
        return  typ,auth,inc_cross,inc_cross_typ,profile,definition,date_to_gate_dict,active_chakras,active_channels_dict, bdate, cdate, variables
    else:
        return date_to_gate_dict

def unpack_single_features(single_result):
    '''
    convert tuple format into dict
    Args:
        single_result(tuple(lists)): hd_key features
    Return:
        return_dict(dict): keys: "typ","auth","inc_cross","profile"
                                 "definition","date_to_gate_dict","active_chakra"
                                 "active_channel"
    '''
    return_dict = {}
    # unpacking multiple calculation values
    return_dict["typ"] = single_result[0]
    return_dict["auth"] = single_result[1] 
    return_dict["inc_cross"] = single_result[2]
    return_dict["inc_cross_typ"] = single_result[3]
    return_dict["profile"] = single_result[4]
    return_dict["definition"] = single_result[5]
    return_dict["date_to_gate_dict"] = single_result[6]
    return_dict["active_chakra"] = single_result[7]
    return_dict["active_channel"] = single_result[8]
    return_dict["birth_date"] = single_result[9]
    return_dict["create_date"] = single_result[10]
    return_dict["variables"] = single_result[11]
    
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
                                 "definition,"date_to_gate_dict","active_chakra"
                                 "active_channel"
    '''
    return_dict = {}
    # unpacking multiple calculation values
    return_dict["typ_list"] = [result[i][0] for i in range (len(result))]
    return_dict["auth_list"] = [result[i][1] for i in range (len(result))]
    return_dict["inc_cross_list"] = [result[i][2] for i in range (len(result))]
    return_dict["inc_cross_typ_list"] = [result[i][3] for i in range (len(result))]
    return_dict["profile_list"] = [result[i][4] for i in range (len(result))]
    return_dict["definition_list"] = [result[i][5] for i in range (len(result))]
    return_dict["date_to_gate_dict"] = [result[i][6] for i in range (len(result))]
    return_dict["active_chakra_list"] = [result[i][7] for i in range (len(result))]
    return_dict["active_channel_list"] = [result[i][8] for i in range (len(result))]
    
    if full:
        #extract date_to_gate_dict lists value keys'lon', 'gate', 'line', 'color', 'tone', 'base'
        return_dict["gate_list"] = [return_dict["date_to_gate_dict"][i]["gate"] 
                                    for i in range(len(return_dict["date_to_gate_dict"]))]
        return_dict["line_list"] = [return_dict["date_to_gate_dict"][i]["line"] 
                                    for i in range(len(return_dict["date_to_gate_dict"]))]
        return_dict["lon_list"] = [return_dict["date_to_gate_dict"][i]["lon"] 
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



def analyze_dynamics_gold(owners_g1, owners_g2):
    """
    Determines the social dynamic of a channel with Gold Standard Codes.
    Returns: (Type Code, Label, Contributors Dict)
    """
    set_g1 = set(o['id'] for o in owners_g1)
    set_g2 = set(o['id'] for o in owners_g2)
    all_participants = set_g1.union(set_g2)
    
    if not set_g1 or not set_g2:
        return "VOID", "Inactive", []
    
    # Check for Solo/Dominant (One person has BOTH gates)
    solo_owners = set_g1.intersection(set_g2)
    
    if len(solo_owners) > 0:
        if len(all_participants) == 1:
             return "DOM", "Solo-Driven", list(solo_owners)
        else:
             return "MIXED", "Mixed (Solo + EM)", list(all_participants)
             
    # Competition Logic (Friction)
    # If multiple people on same gate.
    if len(set_g1) > 1 or len(set_g2) > 1:
        return "COMP", "Electromagnetic with Friction", list(all_participants)

    return "EM", "Electromagnetic", list(all_participants)

def get_penta(participants_data, group_type="family"):
    """
    Gold Standard Penta Analysis (Sovereign Standard)
    Args:
        participants_data: Dict[str, Dict] containing 'gate', 'line', 'label' lists.
        group_type: 'family' or 'business'
    """
    # 1. Initialize Detailed Ownership Map
    gate_ownership = {g: [] for g in hd_constants.PENTA_GATES}
    
    # 2. Parse Inputs
    group_size = len(participants_data)
    
    for person_id, p_data in participants_data.items():
        if isinstance(p_data, list):
            for g in p_data:
                if g in gate_ownership:
                    gate_ownership[g].append({"id": person_id, "polarity": "Unknown", "line": 0})
        elif isinstance(p_data, dict):
            gates = p_data.get("gate", [])
            lines = p_data.get("line", [])
            labels = p_data.get("label", [])
            for i, g in enumerate(gates):
                if g in gate_ownership:
                    lbl = labels[i] if i < len(labels) else "prs"
                    pol = "Design" if lbl == "des" else "Personality"
                    ln = lines[i] if i < len(lines) else 0
                    gate_ownership[g].append({"id": person_id, "polarity": pol, "line": ln})

    # 3. Build Analysis
    penta_anatomy = {
        "upper_penta": {"label": "Direction & Vision", "channels": {}},
        "lower_penta": {"label": "Action & Generation", "channels": {}}
    }
    
    metrics = {
        "total_channels": 0,
        "upper_active": 0,
        "lower_active": 0,
        "bottlenecks": set(),
        "missing_gates_freq": {g: 0 for g in hd_constants.PENTA_GATES},
        "backbone_status": {}
    }

    score_channels_backbone = ["15-5", "2-14", "46-29"]
    active_backbone_count = 0
    functional_roles = {}
    
    # Diamond Standard: Context Swtiching
    if group_type.lower() == "family":
        skills_map = hd_constants.FAMILY_SKILLS_MAP
        shadow_map = hd_constants.FAMILY_SHADOW_MAP
    else:
        # Fallback to current maps if renamed or use legacy if available
        # Check if BUSINESS_SKILLS_MAP exists, else use BG5
        if hasattr(hd_constants, "BUSINESS_SKILLS_MAP"):
            skills_map = hd_constants.BUSINESS_SKILLS_MAP
            shadow_map = hd_constants.BUSINESS_SHADOW_MAP
        else:
            skills_map = hd_constants.BG5_SKILLS_MAP
            shadow_map = hd_constants.BG5_SHADOW_MAP

    for zone_key, zone_def in hd_constants.PENTA_DEFINITIONS.items():
        # zone_key is "upper_penta" etc.

        for ch_key, ch_def in zone_def['channels'].items():
            g1, g2 = ch_def['gates']
            ch_name = ch_def['name']

            owners_g1 = gate_ownership.get(g1, [])
            owners_g2 = gate_ownership.get(g2, [])

            # --- Dynamics ---
            type_code, type_label, drivers = analyze_dynamics_gold(owners_g1, owners_g2)
            is_active = (type_code != "VOID")
            
            # Semantic Context
            skill_g1 = skills_map.get(g1, "Unknown")
            skill_g2 = skills_map.get(g2, "Unknown")
            business_label = f"{skill_g1} & {skill_g2}"

            channel_node = {
                "name": ch_name,
                "business_label": business_label, # Is actually Context Label now
                "status": "Active" if is_active else "Inactive",
                "type": type_code,
                "label": type_label,
                "contributors": {}, 
                "gap_analysis": None
            }
            
            if is_active:
                metrics["total_channels"] += 1
                if zone_key == "upper_penta":
                    metrics["upper_active"] += 1
                if zone_key == "lower_penta":
                    metrics["lower_active"] += 1
                
                if ch_key in score_channels_backbone:
                    active_backbone_count += 1
                    metrics["backbone_status"][ch_key] = "Strong"
                
                # Build Contributors & Functional Roles
                all_participant_ids = set()
                role_players = set()

                def add_contrib(gate, objs):
                    for o in objs:
                        pid = o['id']
                        all_participant_ids.add(pid)
                        role_players.add(pid)
                        if pid not in channel_node["contributors"]:
                             channel_node["contributors"][pid] = {}
                        
                        g_key = f"gate_{gate}"
                        if g_key not in channel_node["contributors"][pid]:
                            channel_node["contributors"][pid][g_key] = {"lines": [], "polarities": set()}
                        
                        channel_node["contributors"][pid][g_key]["lines"].append(o['line'])
                        channel_node["contributors"][pid][g_key]["polarities"].add(o['polarity'])
                        
                        # Sovereign Standard: Line Semantics
                        if "line_labels" not in channel_node["contributors"][pid][g_key]:
                             channel_node["contributors"][pid][g_key]["line_labels"] = []
                        line_desc = hd_constants.PENTA_LINE_KEYWORD_MAP.get(o['line'], "Unknown")
                        channel_node["contributors"][pid][g_key]["line_labels"].append(line_desc)

                add_contrib(g1, owners_g1)
                add_contrib(g2, owners_g2)
                
                # Cleanup Polarities (set -> list)
                for pid in channel_node["contributors"]:
                    for gk in channel_node["contributors"][pid]:
                         channel_node["contributors"][pid][gk]["polarities"] = list(channel_node["contributors"][pid][gk]["polarities"])
                
                # Add to Functional Roles
                if ch_name not in functional_roles:
                    functional_roles[ch_name] = []
                functional_roles[ch_name].extend(list(role_players))
                functional_roles[ch_name] = sorted(list(set(functional_roles[ch_name])))
                
                # Bottlenecks (DOM)
                if type_code == "DOM":
                    for d in drivers:
                        metrics["bottlenecks"].add(d)

            else:
                # Inactive
                if ch_key in score_channels_backbone:
                    metrics["backbone_status"][ch_key] = "Missing"
                
                missing_gates = []
                missing_skills = []
                shadow_themes = []

                if not owners_g1: 
                    missing_gates.append(g1)
                    missing_skills.append(skill_g1)
                    shadow_themes.append(shadow_map.get(g1, "Dysfunction"))
                    metrics["missing_gates_freq"][g1] += 1
                
                if not owners_g2: 
                    missing_gates.append(g2)
                    missing_skills.append(skill_g2)
                    shadow_themes.append(shadow_map.get(g2, "Dysfunction"))
                    metrics["missing_gates_freq"][g2] += 1
                
                channel_node["gap_analysis"] = {
                    "missing_gates": missing_gates,
                    "missing_skills": missing_skills,
                    "shadow_themes": shadow_themes,
                    "severity": "CRITICAL" if ch_key in score_channels_backbone else "MODERATE",
                    "impact": ch_def.get("gap_msg", "Inactive")
                }

            penta_anatomy[zone_key]["channels"][ch_key] = channel_node
    
    # 4. Metrics & Scores
    # Stability: 3/3 = 100, 2/3 = 70, 1/3 = 40, 0 = 10
    score_map = {3: 100, 2: 70, 1: 40, 0: 10}
    stability_score = score_map.get(active_backbone_count, 10)
    
    # Vision Score (Upper Active / 3 * 100)
    vision_score = round((metrics["upper_active"] / 3) * 100)
    # Action Score (Lower Active / 3 * 100)
    # Note: Using 3 as total per zone denominator
    action_score = round((metrics["lower_active"] / 3) * 100)

    # Hiring Logic
    needs = [g for g, c in metrics["missing_gates_freq"].items() if c > 0]
    # Simple sort by ID for stability, or could use frequency
    needs.sort(key=lambda x: metrics["missing_gates_freq"][x], reverse=True)

    response = {
        "meta": {
            "group_size": group_size,
            "penta_formed": 3 <= group_size <= 5,
            "penta_type": group_type.capitalize(),
            "analysis_timestamp": "2026-01-19T00:00:00Z"
        },
        "analytical_metrics": {
            "stability_score": stability_score,
            "vision_score": vision_score,
            "action_score": action_score,
            "bottlenecks": list(metrics["bottlenecks"]),
            "backbone_integrity": metrics["backbone_status"]
        },
        "functional_roles": functional_roles, # Diamond Feature
        "penta_anatomy": penta_anatomy,
        "hiring_logic": {
            "urgent_needs": needs[:3],
            "insight": f"Group has {active_backbone_count}/3 Backbone channels. {'Vision' if vision_score > action_score else 'Action'} dominates."
        }
    }
    
    return response





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
        definition = get_definition(active_channels_dict,active_chakras)
        planets = date_to_gate_dict
        return active_channels_dict,active_chakras,typ,auth,definition,planets

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
                                    "definition","date_to_gate_dict","active_chakra"
                                    "active_channel"
        '''
        return_dict = {}
        # unpacking multiple calculation values

        return_dict["active_channel_list"] = [self.result[i][0] for i in range (len(self.result))]
        return_dict["active_chakra_list"] = [self.result[i][1] for i in range (len(self.result))]
        return_dict["typ_list"] = [self.result[i][2] for i in range (len(self.result))]
        return_dict["auth_list"] = [self.result[i][3] for i in range (len(self.result))]
        return_dict["definition_list"] = [self.result[i][4] for i in range (len(self.result))]
        return_dict["planet_dict_list"] = [self.result[i][5] for i in range (len(self.result))]

        return return_dict
