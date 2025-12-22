"""
synchronize IGING and zodiac circle ->58°
    Human design systems start at gate 41, Aries, (source :Ra Uru BlackBook)
"""
IGING_offset = 58  

# codes from swe-> dict([[i,swe.get_planet_name(i)] for i in range(0,23)])
SWE_PLANET_DICT = {"Sun":0,
                    "Earth":0, # Sun position -180 longitude
                    "Moon":1,
                    "North_Node":11, # Discussion whether mean or True node?! here North Node -> true Node
                    "South_Node":11, # North_Node position -180 longitude
                    "Mercury":2,
                    "Venus":3,
                    "Mars":4,
                    "Jupiter":5,
                    "Saturn":6,
                    "Uranus":7,
                    "Neptune":8,
                    "Pluto":9,
                   #"Chiron":15,
                   #'Pholus':16,
                   #'Ceres':17,
                   #'Pallas':18,
                   #'Juno':19,
                   #'Vesta':20,
                   }
IGING_CIRCLE_LIST =  [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3, 27, 24, 2, 23, 8, 
                      20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56, 31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 
                      46, 18, 48, 57, 32, 50, 28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60]

#legend ->HD=Head,AA=Ajna, TT=Throat, GC=G_Center, SL = Sacral, SN = Spleen, SP = SolarPlexus, RT = Root
GATES_CHAKRA_DICT = {(64,47):("HD","AA"),
                     (61,24):("HD","AA"),
                     (63, 4):("HD","AA"),
                     (17,62):("AA","TT"),
                     (43,23):("AA","TT"),
                     (11,56):("AA","TT"),
                     (16,48):("TT","SN"),
                     (20,57):("TT","SN"),
                     (20,34):("TT","SL"),
                     (20,10):("TT","GC"),
                     (31, 7):("TT","GC"),
                     ( 8, 1):("TT","GC"),
                     (33,13):("TT","GC"),
                     (45,21):("TT","HT"),
                     (35,36):("TT","SP"),
                     (12,22):("TT","SP"),
                     (32,54):("SN","RT"),
                     (28,38):("SN","RT"),
                     (57,34):("SN","SL"),
                     (50,27):("SN","SL"),
                     (18,58):("SN","RT"),
                     (10,34):("GC","SL"),
                     (15, 5):("GC","SL"),
                     ( 2,14):("GC","SL"),
                     (46,29):("GC","SL"),
                     (10,57):("GC","SN"),
                     (25,51):("GC","HT"),
                     (59, 6):("SL","SP"),
                     (42,53):("SL","RT"),
                     ( 3,60):("SL","RT"),
                     ( 9,52):("SL","RT"),
                     (26,44):("HT","SN"),
                     (40,37):("HT","SP"),
                     (49,19):("SP","RT"),
                     (55,39):("SP","RT"),
                     (30,41):("SP","RT"),
                    }

CHAKRA_LIST = ["HD","AA","TT","GC","HT","SP","SN","SL","RT"]

CHAKRA_NAMES_MAP = {
    "HD": "Head",
    "AA": "Ajna",
    "TT": "Throat",
    "GC": "G_Center",
    "SL": "Sacral",
    "SN": "Spleen",
    "SP": "SolarPlexus",
    "RT": "Root",
    "HT": "Heart" # Assuming HT stands for Heart based on common chakra systems and GATES_CHAKRA_DICT
}

INNER_AUTHORITY_NAMES_MAP = {
    "SP": "Solar Plexus",
    "SL": "Sacral",
    "SN": "Spleen",
    "HT": "Heart",
    "GC": "G Center",
    "HT_GC": "Heart & G Center", # Assuming HT_GC is a combination
    "outher": "Outer Authority", # Correcting "outher" to "Outer"
    "unknown?": "Unknown" # Handling "unknown?"
}

CHANNEL_MEANING_DICT = {
                        (64,47):["Abstraction","D. of mental activity and clarity"],
                        (61,24):["Awareness", "D. of a thinker"],
                        (63, 4):["Logic","D. of mental muse? mixed with doubt"],
                        (17,62):["Acceptance","D. of an organizational being"],
                        (43,23):["Structuring","D. of individuality"],
                        (11,56):["Curiosity","D. of a searcher"],
                        (16,48):["The Wave Length","D. of a talent"],
                        (20,57):["The Brain Wave","D. of penetrating awareness"],
                        (20,34):["Charisma","D. where thoughts must become deeds"],
                        (32,54):["Transformation","D. of being driven"],
                        (28,38):["Struggle","D. of stubbornness"],
                        (18,58):["Judgment","D. of insatiability"],
                        (20,10):["Awakening","D. of commitment to higher principles"],
                        (31, 7):["The Alpha","For 'good' or 'bad', a d. of leadership"],
                        ( 8, 1):["Inspiration","The creative role model"],
                        (33,13):["The Prodigal","The d. of witness"],
                        (10,34):["Exploration","A d. of following one's convictions"],
                        (15, 5):["Rhythm","A d. of being in the flow"],
                        ( 2,14):["The Beat","A d. of being the keeper of keys"],
                        (46,29):["Discovery","A d. of succeeding where others fail"],
                        (10,57):["Perfected Form","A d. of survival"],
                        (57,34):["Power","A d. of an archetype"],
                        (50,27):["Preservation","A. d. of custodianship"],
                        (45,21):["Money","A d. of a materialist"],
                        (59, 6):["Mating","A d. focused on reproduction"],
                        (42,53):["Maturation","A d. of balanced development,cyclic"],
                        ( 3,60):["Mutation","Energy which fluctuates and initiates, pulse"],
                        ( 9,52):["Concentration","A d. of determination, focused"],
                        (26,44):["Surrender","A d. of a transmitter"],
                        (25,51):["Initiation","A d. of needing to be first"],
                        (40,37):["Community","A d. of being part, seeking a whole"],
                        (35,36):["Transitoriness","A d. of a 'Jack of all Trades'"],
                        (12,22):["Openness","A d, of a social being"],
                        (49,19):["Synthesis","A d. of being sensitive"],
                        (55,39):["Emoting","A d. of moodiness"],
                        (30,41):["Recognition","A d. of focused energy"],
                        }

IC_CROSS_TYP = { 
                (1,3):"RAC",
                (1,4):"RAC",
                (2,4):"RAC",
                (2,5):"RAC",
                (3,5):"RAC",
                (3,6):"RAC",
                (4,6):"RAC",
                (4,1):"JXP",
                (5,1):"LAC",
                (5,2):"LAC",
                (6,2):"LAC",
                (6,3):"LAC",
                }

penta_dict = {
                31:[],
                8:[],
                33:[],
                7:[],
                1:[],
                13:[],
                15:[],
                2:[],
                46:[],
                5:[],
                14:[],
                29:[]
             }

circuit_typ_dict={
                    (24,61):"Knowledge",
					(23,43):"Knowledge",
					( 1, 8):"Knowledge",
					( 2,14):"Knowledge",
					( 3,60):"Knowledge",
					(39,55):"Knowledge",
					(12,22):"Knowledge",
					(28,38):"Knowledge",
					(20,57):"Knowledge",
					(10,34):"Centre",
					(25,51):"Centre",
					( 4,63):"Realize",
					(17,62):"Realize",
					( 7,31):"Realize",
					( 5,15):"Realize",
					( 9,52):"Realize",
					(18,58):"Realize",
					(16,48):"Realize",
					(47,64):"Sense",
					(11,56):"Sense",
					(13,33):"Sense",
					(29,46):"Sense",
					(42,53):"Sense",
					(30,41):"Sense",
					(35,36):"Sense",
					(32,54):"Ego",
					(26,44):"Ego",
					(19,49):"Ego",
					(37,40):"Ego",
					(21,45):"Ego",
					( 6,59):"Protect",
					(27,50):"Protect",
					(10,20):"Integration",
					(20,34):"Integration",
					(34,57):"Integration",
					(10,57):"Integration",
				 }
circuit_group_typ_dict = {
                        "Knowledge":"Individual",
						"Centre":"Individual",
						"Realize":"Collective",
						"Sense":"Collective",
						"Ego":"Tribal",
						"Protect":"Tribal",
						"Integration":"Integration",
                        }

awareness_stream_dict = {
						(58,18,48,16):"Taste",
						(38,28,67,20):"Intuition",
						(54,32,44,26):"Instinct",
						(41,30,36,35):"Feel",
						(39,55,22,12):"Emotion",
						(19,49,37,40):"Sensitivity",
						(64,47,11,56):"Realize/Meaning",
						(61,24,43,23):"Knowledge",
						(63, 4,17,62):"Understand"
						}
						
awareness_stream_group_dict = {
								"Taste":"Spleen",
								"Intuition":"Spleen",
								"Instinct":"Spleen",
								"Feel":"SolarPlexus",
								"Emotion":"SolarPlexus",
								"Sensitivity":"SolarPlexus",
								"Realize/Meaning":"Ajna",
								"Knowledge":"Ajna",
								"Understand":"Ajna"
								}
								                
# Dictionary Mapping for Incarnation Crosses:
# Key: Personality Sun Gate (Integer)
# Value: Dictionary { "RAC": "Right Angle...", "JC": "Juxtaposition...", "LAC": "Left Angle..." }

CROSS_DB = {
				# --- Quarter of Initiation (Purpose via Mind) ---
				13: {"RAC": "The Right Angle Cross of the Sphinx (1)", "JC": "The Juxtaposition Cross of Listening", "LAC": "The Left Angle Cross of Masks (1)"},
				49: {"RAC": "The Right Angle Cross of Explanation (1)", "JC": "The Juxtaposition Cross of Principles", "LAC": "The Left Angle Cross of Revolution (1)"},
				30: {"RAC": "The Right Angle Cross of Contagion (1)", "JC": "The Juxtaposition Cross of Fates", "LAC": "The Left Angle Cross of Industry (1)"},
				55: {"RAC": "The Right Angle Cross of the Sleeping Phoenix (1)", "JC": "The Juxtaposition Cross of Moods", "LAC": "The Left Angle Cross of Spirit (1)"},
				37: {"RAC": "The Right Angle Cross of Planning (1)", "JC": "The Juxtaposition Cross of Bargains", "LAC": "The Left Angle Cross of Migration (1)"},
				63: {"RAC": "The Right Angle Cross of Consciousness (1)", "JC": "The Juxtaposition Cross of Doubts", "LAC": "The Left Angle Cross of Dominion (1)"},
				22: {"RAC": "The Right Angle Cross of Rulership (1)", "JC": "The Juxtaposition Cross of Grace", "LAC": "The Left Angle Cross of Informing (1)"},
				36: {"RAC": "The Right Angle Cross of the Eden (1)", "JC": "The Juxtaposition Cross of Crisis", "LAC": "The Left Angle Cross of the Plane (1)"},
				25: {"RAC": "The Right Angle Cross of the Vessel of Love (1)", "JC": "The Juxtaposition Cross of Innocence", "LAC": "The Left Angle Cross of Healing (1)"},
				17: {"RAC": "The Right Angle Cross of Service (1)", "JC": "The Juxtaposition Cross of Opinions", "LAC": "The Left Angle Cross of Upheaval (1)"},
				21: {"RAC": "The Right Angle Cross of Tension (1)", "JC": "The Juxtaposition Cross of Control", "LAC": "The Left Angle Cross of Endeavor (1)"},
				51: {"RAC": "The Right Angle Cross of Penetration (1)", "JC": "The Juxtaposition Cross of Shock", "LAC": "The Left Angle Cross of the Clarion (1)"},
				42: {"RAC": "The Right Angle Cross of the Maya (1)", "JC": "The Juxtaposition Cross of Completion", "LAC": "The Left Angle Cross of Limitation (1)"},
				3:  {"RAC": "The Right Angle Cross of Laws (1)", "JC": "The Juxtaposition Cross of Mutation", "LAC": "The Left Angle Cross of Wishes (1)"},
				27: {"RAC": "The Right Angle Cross of the Unexpected (1)", "JC": "The Juxtaposition Cross of Caring", "LAC": "The Left Angle Cross of Alignment (1)"},
				24: {"RAC": "The Right Angle Cross of the Four Ways (1)", "JC": "The Juxtaposition Cross of Rationalization", "LAC": "The Left Angle Cross of Incarnation (1)"},

				# --- Quarter of Civilization (Purpose via Form) ---
				2:  {"RAC": "The Right Angle Cross of the Sphinx (2)", "JC": "The Juxtaposition Cross of the Driver", "LAC": "The Left Angle Cross of Defiance (1)"},
				23: {"RAC": "The Right Angle Cross of Explanation (2)", "JC": "The Juxtaposition Cross of Assimilation", "LAC": "The Left Angle Cross of Dedication (1)"},
				8:  {"RAC": "The Right Angle Cross of Contagion (2)", "JC": "The Juxtaposition Cross of Contribution", "LAC": "The Left Angle Cross of Uncertainty (1)"},
				20: {"RAC": "The Right Angle Cross of the Sleeping Phoenix (2)", "JC": "The Juxtaposition Cross of the Now", "LAC": "The Left Angle Cross of Duality (1)"},
				16: {"RAC": "The Right Angle Cross of Planning (2)", "JC": "The Juxtaposition Cross of Experimentation", "LAC": "The Left Angle Cross of Identification (1)"},
				35: {"RAC": "The Right Angle Cross of Consciousness (2)", "JC": "The Juxtaposition Cross of Experience", "LAC": "The Left Angle Cross of Separation (1)"},
				45: {"RAC": "The Right Angle Cross of Rulership (2)", "JC": "The Juxtaposition Cross of Possession", "LAC": "The Left Angle Cross of Confrontation (1)"},
				12: {"RAC": "The Right Angle Cross of the Eden (2)", "JC": "The Juxtaposition Cross of Articulation", "LAC": "The Left Angle Cross of Education (1)"},
				15: {"RAC": "The Right Angle Cross of the Vessel of Love (2)", "JC": "The Juxtaposition Cross of Extremes", "LAC": "The Left Angle Cross of Prevention (1)"},
				52: {"RAC": "The Right Angle Cross of Service (2)", "JC": "The Juxtaposition Cross of Stillness", "LAC": "The Left Angle Cross of Demands (1)"},
				39: {"RAC": "The Right Angle Cross of Tension (2)", "JC": "The Juxtaposition Cross of Provocation", "LAC": "The Left Angle Cross of Individualism (1)"},
				53: {"RAC": "The Right Angle Cross of Penetration (2)", "JC": "The Juxtaposition Cross of Beginnings", "LAC": "The Left Angle Cross of Cycles (1)"},
				62: {"RAC": "The Right Angle Cross of the Maya (2)", "JC": "The Juxtaposition Cross of Detail", "LAC": "The Left Angle Cross of Obscuration (1)"},
				56: {"RAC": "The Right Angle Cross of Laws (2)", "JC": "The Juxtaposition Cross of Stimulation", "LAC": "The Left Angle Cross of Distraction (1)"},
				31: {"RAC": "The Right Angle Cross of the Unexpected (2)", "JC": "The Juxtaposition Cross of Influence", "LAC": "The Left Angle Cross of the Alpha (1)"},
				33: {"RAC": "The Right Angle Cross of the Four Ways (2)", "JC": "The Juxtaposition Cross of Retreat", "LAC": "The Left Angle Cross of Refinement (1)"},

				# --- Quarter of Duality (Purpose via Bonding) ---
				7:  {"RAC": "The Right Angle Cross of the Sphinx (3)", "JC": "The Juxtaposition Cross of Interaction", "LAC": "The Left Angle Cross of Masks (2)"},
				4:  {"RAC": "The Right Angle Cross of Explanation (3)", "JC": "The Juxtaposition Cross of Formulation", "LAC": "The Left Angle Cross of Revolution (2)"},
				29: {"RAC": "The Right Angle Cross of Contagion (3)", "JC": "The Juxtaposition Cross of Commitment", "LAC": "The Left Angle Cross of Industry (2)"},
				59: {"RAC": "The Right Angle Cross of the Sleeping Phoenix (3)", "JC": "The Juxtaposition Cross of Strategy", "LAC": "The Left Angle Cross of Spirit (2)"},
				40: {"RAC": "The Right Angle Cross of Planning (3)", "JC": "The Juxtaposition Cross of Denial", "LAC": "The Left Angle Cross of Migration (2)"},
				64: {"RAC": "The Right Angle Cross of Consciousness (3)", "JC": "The Juxtaposition Cross of Confusion", "LAC": "The Left Angle Cross of Dominion (2)"},
				47: {"RAC": "The Right Angle Cross of Rulership (3)", "JC": "The Juxtaposition Cross of Oppression", "LAC": "The Left Angle Cross of Informing (2)"},
				6:  {"RAC": "The Right Angle Cross of the Eden (3)", "JC": "The Juxtaposition Cross of Conflict", "LAC": "The Left Angle Cross of the Plane (2)"},
				46: {"RAC": "The Right Angle Cross of the Vessel of Love (3)", "JC": "The Juxtaposition Cross of Serendipity", "LAC": "The Left Angle Cross of Healing (2)"},
				18: {"RAC": "The Right Angle Cross of Service (3)", "JC": "The Juxtaposition Cross of Correction", "LAC": "The Left Angle Cross of Upheaval (2)"},
				48: {"RAC": "The Right Angle Cross of Tension (3)", "JC": "The Juxtaposition Cross of Depth", "LAC": "The Left Angle Cross of Endeavor (2)"},
				57: {"RAC": "The Right Angle Cross of Penetration (3)", "JC": "The Juxtaposition Cross of Intuition", "LAC": "The Left Angle Cross of the Clarion (2)"},
				32: {"RAC": "The Right Angle Cross of the Maya (3)", "JC": "The Juxtaposition Cross of Conservation", "LAC": "The Left Angle Cross of Limitation (2)"},
				50: {"RAC": "The Right Angle Cross of Laws (3)", "JC": "The Juxtaposition Cross of Values", "LAC": "The Left Angle Cross of Wishes (2)"},
				28: {"RAC": "The Right Angle Cross of the Unexpected (3)", "JC": "The Juxtaposition Cross of Risks", "LAC": "The Left Angle Cross of Alignment (2)"},
				44: {"RAC": "The Right Angle Cross of the Four Ways (3)", "JC": "The Juxtaposition Cross of Alertness", "LAC": "The Left Angle Cross of Incarnation (2)"},

				# --- Quarter of Mutation (Purpose via Transformation) ---
				1:  {"RAC": "The Right Angle Cross of the Sphinx (4)", "JC": "The Juxtaposition Cross of Self-Expression", "LAC": "The Left Angle Cross of Defiance (2)"},
				43: {"RAC": "The Right Angle Cross of Explanation (4)", "JC": "The Juxtaposition Cross of Insight", "LAC": "The Left Angle Cross of Dedication (2)"},
				14: {"RAC": "The Right Angle Cross of Contagion (4)", "JC": "The Juxtaposition Cross of Empowering", "LAC": "The Left Angle Cross of Uncertainty (2)"},
				34: {"RAC": "The Right Angle Cross of the Sleeping Phoenix (4)", "JC": "The Juxtaposition Cross of Power", "LAC": "The Left Angle Cross of Duality (2)"},
				9:  {"RAC": "The Right Angle Cross of Planning (4)", "JC": "The Juxtaposition Cross of Focus", "LAC": "The Left Angle Cross of Identification (2)"},
				5:  {"RAC": "The Right Angle Cross of Consciousness (4)", "JC": "The Juxtaposition Cross of Habits", "LAC": "The Left Angle Cross of Separation (2)"},
				26: {"RAC": "The Right Angle Cross of Rulership (4)", "JC": "The Juxtaposition Cross of the Trickster", "LAC": "The Left Angle Cross of Control (2)"},
				11: {"RAC": "The Right Angle Cross of the Eden (4)", "JC": "The Juxtaposition Cross of Ideas", "LAC": "The Left Angle Cross of Education (2)"},
				10: {"RAC": "The Right Angle Cross of the Vessel of Love (4)", "JC": "The Juxtaposition Cross of Behavior", "LAC": "The Left Angle Cross of Prevention (2)"},
				58: {"RAC": "The Right Angle Cross of Service (4)", "JC": "The Juxtaposition Cross of Vitality", "LAC": "The Left Angle Cross of Demands (2)"},
				38: {"RAC": "The Right Angle Cross of Tension (4)", "JC": "The Juxtaposition Cross of Opposition", "LAC": "The Left Angle Cross of Individualism (2)"},
				54: {"RAC": "The Right Angle Cross of Penetration (4)", "JC": "The Juxtaposition Cross of Ambition", "LAC": "The Left Angle Cross of Cycles (2)"},
				61: {"RAC": "The Right Angle Cross of the Maya (4)", "JC": "The Juxtaposition Cross of Thinking", "LAC": "The Left Angle Cross of Obscuration (2)"},
				60: {"RAC": "The Right Angle Cross of Laws (4)", "JC": "The Juxtaposition Cross of Limitation", "LAC": "The Left Angle Cross of Distraction (2)"},
				41: {"RAC": "The Right Angle Cross of the Unexpected (4)", "JC": "The Juxtaposition Cross of Fantasy", "LAC": "The Left Angle Cross of the Alpha (2)"},
				19: {"RAC": "The Right Angle Cross of the Four Ways (4)", "JC": "The Juxtaposition Cross of Need", "LAC": "The Left Angle Cross of Refinement (2)"}
}

PROFILE_DB = {
				(1, 3): "1/3: Investigator Martyr",
				(1, 4): "1/4: Investigator Opportunist",
				(2, 4): "2/4: Hermit Opportunist",
				(2, 5): "2/5: Hermit Heretic",
				(3, 5): "3/5: Martyr Heretic",
				(3, 6): "3/6: Martyr Role Model",
				(4, 6): "4/6: Opportunist Role Model",
				(4, 1): "4/1: Opportunist Investigator",
				(5, 1): "5/1: Heretic Investigator",
				(5, 2): "5/2: Heretic Hermit",
				(6, 2): "6/2: Role Model Hermit",
				(6, 3): "6/3: Role Model Martyr"
}

CHANNEL_DB = {
				# Integration Channels
				"20/34": "The Channel of Charisma (A Design of Thoughts Becoming Deeds)",
				"10/34": "The Channel of Exploration (A Design of Following One's Convictions)",
				"10/20": "The Channel of Awakening (A Design of Commitment to Higher Principles)",
				"20/57": "The Channel of the Brainwave (A Design of Penetrating Awareness)",
				"10/57": "The Channel of Perfected Form (A Design for Survival)",
				"34/57": "The Channel of Power (A Design of an Archetype)",

				# Individual Circuitry (Knowing)
				"24/61": "The Channel of Awareness (A Design of a Thinker)",
				"23/43": "The Channel of Structuring (A Design of Individuality 'Genius to Freak')",
				"28/38": "The Channel of Struggle (A Design of Stubbornness)",
				"39/55": "The Channel of Emoting (A Design of Moodiness)",
				"12/22": "The Channel of Openness (A Design of a Social Being)",
				"3/60":  "The Channel of Mutation (Energy that Generates and Initiates)",
				"2/14":  "The Channel of the Beat (A Design of Being the Key Keeper)",
				"1/8":   "The Channel of Inspiration (A Design of a Creative Role Model)",

				# Individual Circuitry (Centering)
				"25/51": "The Channel of Initiation (A Design of Needing to be First)",

				# Collective Circuitry (Logic/Understanding)
				"4/63":  "The Channel of Logic (A Design of Mental Ease Mixed with Doubt)",
				"17/62": "The Channel of Acceptance (A Design of an Organizational Being)",
				"18/58": "The Channel of Judgment (A Design of Insatiability)",
				"9/52":  "The Channel of Concentration (A Design of Determination)",
				"5/15":  "The Channel of Rhythm (A Design of Being in the Flow)",
				"7/31":  "The Channel of the Alpha (A Design of Leadership for 'Good' or 'Bad')",
				"16/48": "The Channel of the Wavelength (A Design of Talent)",

				# Collective Circuitry (Sensing/Abstract)
				"47/64": "The Channel of Abstraction (A Design of Mental Activity and Clarity)",
				"11/56": "The Channel of Curiosity (A Design of a Searcher)",
				"42/53": "The Channel of Maturation (A Design of Balanced Development)",
				"29/46": "The Channel of Discovery (A Design of Succeeding Where Others Fail)",
				"13/33": "The Channel of the Prodigal (A Design of a Witness)",
				"30/41": "The Channel of Recognition (A Design of Focused Energy)",
				"35/36": "The Channel of Transitoriness (A Design of a 'Jack of All Trades')",

				# Tribal Circuitry (Ego)
				"32/54": "The Channel of Transformation (A Design of Being Driven)",
				"26/44": "The Channel of Surrender (A Design of a Transmitter)",
				"19/49": "The Channel of Synthesis (A Design of Being Sensitive)",
				"37/40": "The Channel of Community (A Design of a Part Seeking a Whole)",
				"21/45": "The Channel of Money (A Design of a Materialist)",
				
				# Tribal Circuitry (Defense)
				"6/59":  "The Channel of Mating (A Design Focused on Reproduction)",
				"27/50": "The Channel of Preservation (A Design of Custodianship)"
}

DEFINITION_DB = {
				"0": "No Definition (Reflector)",  # Rare case, strictly for Reflectors
				"1": "Single Definition",          # All defined centers are connected
				"2": "Split Definition",           # Two separate areas of definition
				"3": "Triple Split Definition",    # Three separate areas of definition
				"4": "Quadruple Split Definition"  # Four separate areas of definition
}

# hd_constants.py or configuration section

TYPE_DETAILS_MAP = {
    "Manifestor": {
        "strategy": "To Inform",
        "signature": "Peace",
        "not_self": "Anger",
        "aura": "Closed & Repelling"
    },
    "Generator": {
        "strategy": "Wait to Respond",
        "signature": "Satisfaction",
        "not_self": "Frustration",
        "aura": "Open & Enveloping"
    },
    "Manifesting Generator": {
        "strategy": "Wait to Respond", 
        "signature": "Satisfaction",
        # Updated to reflect the hybrid nature (Frustration from Generator side, Anger from Manifestor side)
        "not_self": "Frustration & Anger", 
        "aura": "Open & Enveloping"
    },
    "Projector": {
        "strategy": "Wait for the Invitation",
        "signature": "Success",
        "not_self": "Bitterness",
        "aura": "Focused & Absorbing"
    },
    "Reflector": {
        "strategy": "Wait a Lunar Cycle",
        "signature": "Surprise",
        "not_self": "Disappointment",
        "aura": "Sampling & Resistant"
    },
    # Fallback for errors
    "Unknown": {
        "strategy": "Unknown",
        "signature": "Unknown",
        "not_self": "Unknown",
        "aura": "Unknown"
    }
}