"""
Sample Industrial Dataset Generator for 1,000-Row Sparse Input Testing
Generates realistic industrial automation parts across major manufacturers.
"""

import os
import random
import pandas as pd

SAMPLE_BRANDS = [
    {
        "E1": "ALLEN BRADLEY",
        "Unilog": "Allen-Bradley",
        "DIB": "ROCKWELL",
        "Manuf": "Rockwell Automation",
        "patterns": [
            ("140U-J0D3-C40", "CIR BRKR 40A 3P 600V MOLDED CASE"),
            ("100-C09EJ01", "CONTACTOR 9A 24VDC 1NC 3P IEC"),
            ("800T-A1A", "PUSHBUTTON 30.5MM MOMENTARY BLACK FLUSH"),
            ("700-HA32A24", "RELAY 24VAC 10A 2PDT OCTAL TUBE"),
            ("42EF-D1MNAK-A2", "PHOTOSENSOR RETRO 24VDC NPN/PNP 2M"),
            ("1756-L83E", "CONTROLLOGIX 5580 CONTROLLER 10MB"),
            ("5069-IB16", "COMPACT 5000 16PT 24VDC INPUT MODULE"),
            ("25B-D010N104", "POWERFLEX 525 VFD 5HP 480VAC 3PH"),
            ("140G-G6C3-C50", "MOLDED CASE CIR BRKR 50A 3P 480V"),
            ("193-EEB", "ELECTRONIC OVERLOAD RELAY 1-5A")
        ]
    },
    {
        "E1": "SQUARE D",
        "Unilog": "Schneider Electric",
        "DIB": "SQUARED",
        "Manuf": "Schneider Electric",
        "patterns": [
            ("QO120", "CIR BRKR 20A 1P 120V PLUG-IN 10KA"),
            ("QO3100", "CIR BRKR 100A 3P 240V PLUG-IN 10KA"),
            ("LC1D25BD", "CONTACTOR 25A 24VDC 3P TEESYS D"),
            ("XB4BA21", "PUSHBUTTON 22MM FLUSH BLACK SPRING RETURN"),
            ("RPM31BD", "POWER RELAY 15A 3PDT 24VDC WITH LED"),
            ("XMLB010A2S12", "PRESSURE SWITCH 10 BAR ADJUSTABLE SCALE"),
            ("TM221CE16R", "MODICON M221 PLC 16 IO RELAY ETHERNET"),
            ("ATV320U15N4B", "ALTIVAR 320 VFD 2HP 480V 3PH COMPACT"),
            ("PKF16M434", "PRATIKE INDUSTRIAL PLUG 16A 3P+E 400V IP44"),
            ("LADN22", "AUXILIARY CONTACT BLOCK 2NO+2NC TEESYS")
        ]
    },
    {
        "E1": "SIEMENS",
        "Unilog": "Siemens AG",
        "DIB": "SIEMENS",
        "Manuf": "Siemens Industry",
        "patterns": [
            ("3RV2011-1AA10", "CIR BRKR SIZE S00 FOR MOTOR PROT 0.9-1.25A"),
            ("3RT2015-1BB41", "POWER CONTACTOR 7A 24VDC 3P S00 SCREW"),
            ("3SU1000-0AB10-0AA0", "PUSHBUTTON 22MM ROUND PLASTIC BLACK FLUSH"),
            ("6ES7214-1AG40-0XB0", "SIMATIC S7-1200 CPU 1214C DC/DC/DC 14DI/10DQ/2AI"),
            ("6SL3210-1KE13-2UB2", "SINAMICS G120C 1.5KW 400V 3AC PROFINET"),
            ("3RU2116-1BB0", "THERMAL OVERLOAD RELAY 1.4-2.0A SIZE S00"),
            ("6EP1333-2BA20", "SITOP POWER SUPPLY 24VDC 5A 120/230VAC"),
            ("3SE5112-0CD02", "LIMIT SWITCH METAL ENCLOSURE ROLLER PLUNGER"),
            ("3VA5110-4EC31-0AA0", "MOLDED CASE CIR BRKR 100A 3P 480V 25KA"),
            ("6GK5005-0BA00-1AB2", "SCALANCE X005 UNMANAGED IE SWITCH 5 RJ45")
        ]
    },
    {
        "E1": "EATON",
        "Unilog": "Eaton Bussmann",
        "DIB": "CUTLER-HAMMER",
        "Manuf": "Eaton",
        "patterns": [
            ("FNQ-R-10", "CLASS CC TIME DELAY FUSE 10A 600V"),
            ("KTK-R-15", "CLASS CC FAST ACTING FUSE 15A 600V"),
            ("LPJ-30SP", "LOW-PEAK TIME DELAY FUSE 30A 600V DUAL ELEM"),
            ("BAB3030H", "CIR BRKR 30A 3P 240V BOLT-ON 10KA"),
            ("XTCE018C10TD", "CONTACTOR 18A 24VDC 1NO 3P FRAME C"),
            ("M22-D-G", "PUSHBUTTON 22.5MM NON-ILLUM GREEN FLUSH"),
            ("E57-18LE12-A", "PROX SENSOR INDUCTIVE M18 12MM NPN NO"),
            ("C25DNF340A", "DEFINITE PURPOSE CONTACTOR 40A 3P 120VAC"),
            ("DG1-34012FB-C21C", "POWERXL DG1 VFD 7.5HP 480V IP21"),
            ("PSG240E24RM", "POWER SUPPLY 24VDC 10A 240W DIN RAIL")
        ]
    },
    {
        "E1": "ABB",
        "Unilog": "ABB Installation",
        "DIB": "BALDOR",
        "Manuf": "ABB Inc",
        "patterns": [
            ("S203-C20", "MINIATURE CIR BRKR 20A 3P 480Y/277V C CURVE"),
            ("AF16-30-10-13", "CONTACTOR 16A 100-250VAC/DC 3P 1NO"),
            ("ACS380-040S-02A6-4", "MACHINERY DRIVE 1HP 480V 3PH IP20"),
            ("EM3558T", "BALDOR RELIANCE MOTOR 3HP 1800RPM 3PH 56C TEFC"),
            ("OT16F3", "DISCONNECT SWITCH 3P 16A DOOR MOUNT"),
            ("CP1-10G-10", "PUSHBUTTON 22MM COMPACT GREEN FLUSH 1NO"),
            ("TA25DU-11", "THERMAL OVERLOAD RELAY 7.5-11A FOR AF09-AF38"),
            ("CP-E 24/2.5", "POWER SUPPLY 24VDC 2.5A 100-240VAC IN"),
            ("CR-M024DC4", "PLUG-IN MINIATURE RELAY 4PDT 6A 24VDC"),
            ("XT2N 125 EKIP LS/I IN=25A", "TMAX XT2 CIR BRKR 25A 3P 600V")
        ]
    },
    {
        "E1": "HONEYWELL",
        "Unilog": "Honeywell Sensing",
        "DIB": "HONEYWELL",
        "Manuf": "Honeywell International",
        "patterns": [
            ("SZL-VL-S-J", "MINIATURE LIMIT SWITCH CROSS ROLLER PLUNGER"),
            ("24PCEFA6G", "PRESSURE SENSOR 0-0.5 PSI GAUGE PCB MOUNT"),
            ("GLAC01A1B", "GLOBAL LIMIT SWITCH 1NC/1NO SPDT SNAP ACTION"),
            ("AML21BBA2AA", "PUSHBUTTON PUSH-ON/PUSH-OFF SQUARE ILLUM"),
            ("SS49E", "LINEAR HALL EFFECT SENSOR 3-PIN RADIAL"),
            ("PX2AN1XX150PSAAX", "HEAVY DUTY PRESSURE TRANSDUCER 150 PSI"),
            ("14CE2-1", "COMPACT ENCLOSED SWITCH ROLLER PLUNGER 1M"),
            ("MICRO SWITCH BZ-2RW82-A2", "PREMIUM LARGE BASIC SWITCH SPDT 15A 125V"),
            ("HIH-4000-001", "HUMIDITY SENSOR ANALOG VOLTAGE OUTPUT"),
            ("CSNE151-100", "CLOSED LOOP CURRENT SENSOR 25A PCB MOUNT")
        ]
    },
    {
        "E1": "PARKER",
        "Unilog": "Parker Hannifin",
        "DIB": "PARKER",
        "Manuf": "Parker Hannifin",
        "patterns": [
            ("P2LBX512ESNDDB49", "VALVE SOLENOID 24VDC 5/2 WAY 1/4 NPT"),
            ("06F22AC", "PNEUMATIC FILTER 1/4 NPT 5 MICRON COMPACT"),
            ("06R213AC", "PNEUMATIC REGULATOR 1/4 NPT 0-125 PSI"),
            ("06L22AC", "PNEUMATIC LUBRICATOR 1/4 NPT STANDARD MIST"),
            ("MA33D-1/4", "PRESSURE GAUGE 0-160 PSI 1/4 NPT BACK MOUNT"),
            ("341N01", "VALVE SOLENOID 2-WAY NC 1/4 NPT BRASS 120V"),
            ("PL-4-2", "PUSH-TO-CONNECT FITTING 1/4 TUBE X 1/8 NPT MALE"),
            ("PS1-E111", "PNEUMATIC PRESSURE SWITCH 1-10 BAR DIN CONNECTOR"),
            ("DX1-411-BL49", "ISO 5599-1 SIZE 1 VALVE 5/2 SINGLE SOLENOID 24VDC"),
            ("F442-10-10", "HYDRAULIC HOSE FITTING FEMALE JIC 5/8 TUBE")
        ]
    }
]

def generate_sample_csv(output_path: str = "data/sample_industrial_input.csv", total_rows: int = 1000) -> str:
    """Generates a representative 1,000-row sample input CSV with realistic variations."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    rows = []
    brand_pool = SAMPLE_BRANDS
    
    for i in range(total_rows):
        brand_item = brand_pool[i % len(brand_pool)]
        patterns = brand_item["patterns"]
        base_pn, base_desc = patterns[i % len(patterns)]
        
        # Inject realistic variety in part numbers and suffixes
        suffix_idx = (i // len(brand_pool)) + 1
        mfg_part_num = f"{base_pn}" if suffix_idx <= 10 else f"{base_pn}-{suffix_idx:02d}"
        
        # Occasionally perturb brands to simulate sparse / inconsistent records
        noise_mode = i % 10
        if noise_mode == 0:
            e1 = brand_item["E1"]
            unilog = ""
            dib = brand_item["DIB"]
            manuf = brand_item["Manuf"]
        elif noise_mode == 1:
            e1 = ""
            unilog = brand_item["Unilog"]
            dib = ""
            manuf = brand_item["Manuf"]
        elif noise_mode == 2:
            e1 = brand_item["E1"]
            unilog = brand_item["Unilog"]
            dib = ""
            manuf = ""
        else:
            e1 = brand_item["E1"]
            unilog = brand_item["Unilog"]
            dib = brand_item["DIB"]
            manuf = brand_item["Manuf"]

        rows.append({
            "Mfg_Part_Num": mfg_part_num,
            "Part_Desc": base_desc,
            "E1_Brand": e1,
            "Unilog_Brand": unilog,
            "DIB_Brand": dib,
            "Part_Manuf": manuf
        })

    df = pd.DataFrame(rows, columns=["Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf"])
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} sample rows at {output_path}")
    return output_path

if __name__ == "__main__":
    generate_sample_csv()
