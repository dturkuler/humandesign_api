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
            if report == True:
                print("birth date: "+ bdate)
                print("create date: " + cdate)
                print("energy-type: {}".format(typ))
                print("inner authority: {}".format(auth))
                print("inc. cross: {}".format(inc_cross))
                print("profile: {}/{}".format( *profile, sep='/'))
                print("active chakras: {}".format(active_chakras))
                print("definition: {}".format(definition))
                print("variables: {}".format(variables))
                display(pd.DataFrame(date_to_gate_dict))
                display(pd.DataFrame(active_channels_dict))
         
    if day_chart_only==False:
        return  typ,auth,inc_cross,inc_cross_typ,profile,definition,date_to_gate_dict,active_chakras,active_channels_dict, bdate, cdate
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
    penta_dict = {k: [] for k in hd_constants.penta_dict.keys()}
    
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
    
    # Prepare details dict
    # Convert dataframe-like boolean structure to simple dict
    # We want to know for each penta gate, is it active? And maybe who activates it?
    # The existing logic builds `penta_dict` where values are lists of persons.
    # So `penta_dict` itself is the details dict.
    
    if report:
        df = pd.DataFrame(result_dict) 
        df.loc[df.shape[0]+1,:] = [any(df[col]) for col in df.columns]
        df = df.replace({False:"o",True:"x"})
        df["index"] = list(persons_dict.keys())+["all"]
        df = df.set_index("index",drop=True)
        print(df)
        
    percentage = round(sum_penta_gates/12*100,2)
    return percentage, penta_dict



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
