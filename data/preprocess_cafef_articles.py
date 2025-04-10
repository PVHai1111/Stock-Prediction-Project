import json
import re
from datetime import datetime
from unidecode import unidecode

# === Danh sách mã cổ phiếu (có thể mở rộng thêm) ===
vietnam_tickers = {"AAH", "AAM", "AAT", "ABB", "ABC", "ABI", "ABR", "ABT", "ACB", "ACL", "ACV", "ADC", "ADG", "ADS", "AFX", "AG1", "AGF", "AGG", "AGM", "AGR", "AIC", "ALT", "AMD", "AME", "AMV", "ANT", "ANV", "APC", "APF", "APG", "API", "APS", "APT", "ARM", "ART", "ASG", "ASP", "AST", "ATS", "AVC", "BAB", "BAF", "BAX", "BBC", "BCB", "BCE", "BCF", "BCG", "BCM", "BCP", "BCV", "BDB", "BDF", "BDG", "BED", "BHA", "BHN", "BIC", "BID", "BLF", "BLI", "BLN", "BLT", "BMG", "BMI", "BMV1", "BNA", "BRC", "BRR", "BRS", "BSA", "BSC", "BSG", "BSI", "BSL", "BSR", "BST", "BTH", "BTP", "BTT", "BTV", "BVB", "BVG", "BVH", "BVS", "C47", "C4G", "C69", "C92", "CAB", "CAD", "CAG", "CAN", "CAP", "CAT", "CAV", "CCA", "CCL", "CCP", "CCR", "CCT", "CDC", "CDN", "CDR", "CEC", "CEE", "CEO", "CHP", "CIA", "CIG", "CII", "CJC", "CKG", "CKV", "CLL", "CLM", "CLX", "CMF", "CMG", "CMN", "CMP", "CMS", "CMT", "CMV", "CMX", "CNG", "COM", "CPC", "CPH", "CRE", "CSC", "CSM", "CST", "CTC", "CTD", "CTF", "CTG", "CTI", "CTM", "CTR", "CTS", "CTX", "CX8", "CXH", "D11", "D2D", "DAD", "DAE", "DAH", "DAR", "DAT", "DBC", "DBD", "DBH", "DBM", "DBT", "DC2", "DC4", "DCG", "DCI", "DCL", "DDG", "DDM", "DDN", "DGW", "DHD", "DHG", "DHP", "DHT", "DIG", "DIH", "DL1", "DLD", "DLT", "DM7", "DMC", "DNA", "DNB", "DNH", "DNL", "DNM", "DNS", "DNT", "DNY", "DP2", "DP3", "DPG", "DPP", "DPR", "DRC", "DRG", "DRH", "DRI", "DRL", "DS3", "DSN", "DSP", "DST", "DTA", "DTD", "DTE", "DTG", "DTI", "DTK", "DTL", "DVC", "DVN", "DVP", "DXG", "DXL", "DXP", "EAD", "EBA", "EBS", "ECI", "EIB", "EIC", "EID", "EIN", "ELC", "EMC", "EMG", "EMS", "EPH", "EVE", "EVG", "EVS", "FCN", "FCS", "FDC", "FHN", "FHS", "FIR", "FMC", "FOC", "FPT", "FRT", "FTS", "G20", "G36", "GAS", "GCB", "GE2", "GEE", "GEG", "GEX", "GHC", "GIC", "GIL", "GLT", "GMC", "GMD", "GQN", "GSM", "GSP", "GTN", "GTT", "GVR", "HAB", "HAD", "HAH", "HAR", "HAS", "HAT", "HAV", "HAX", "HBC", "HBS", "HCB", "HCM", "HCT", "HDB", "HDC", "HDG", "HDM", "HDO", "HDP", "HEM", "HES", "HEV", "HFC", "HFS", "HFX", "HHC", "HHG", "HHV", "HIG", "HJS", "HKB", "HLA", "HLC", "HLD", "HLE", "HLS", "HMC", "HMH", "HNA", "HND", "HNG", "HNI", "HNT", "HOT", "HPD", "HPG", "HPT", "HPX", "HQC", "HRC", "HRG", "HRT", "HSG", "HSM", "HSV", "HTC", "HTG", "HTI", "HTN", "HTP", "HTV", "HU1", "HU3", "HUB", "HUG", "HUT", "HVH", "HVN", "IBD", "IBN", "ICF", "ICG", "ICT", "IDI", "IDJ", "IDV", "IFS", "IHK", "IJC", "ILB", "IMP", "IN4", "IPH", "IRC", "ISH", "IST", "ITA", "ITC", "ITD", "ITS", "IVS", "JOS", "JVC", "KBC", "KDC", "KDH", "KHP", "KHS", "KIP", "KKC", "KLB", "KLF", "KMR", "KMT", "KOS", "KSE", "KST", "KTC", "KTS", "KTT", "L10", "L14", "L18", "L35", "L40", "L43", "L61", "L62", "LAF", "LBC", "LBE", "LCD", "LCG", "LCS", "LDG", "LDP", "LEC", "LGC", "LGL", "LGM", "LHC", "LHG", "LIG", "LM7", "LM8", "LMH", "LPB", "LSS", "LUT", "M10", "MAC", "MAS", "MBB", "MBS", "MCH", "MCO", "MDC", "MDN", "MEL", "MFS", "MGG", "MHC", "MIG", "MKT", "MKV", "MNB", "MPC", "MPT", "MSB", "MSH", "MSN", "MST", "MTC", "MTP", "MTS", "MVN", "MVY", "MWG", "NAB", "NAF", "NAP", "NAS", "NBB", "NBC", "NBE", "NBP", "NCS", "NCT", "ND2", "NDC", "NDN", "NDP", "NDT", "NDX", "NED", "NGC", "NHA", "NJC", "NKG", "NLG", "NPS", "NRC", "NT2", "NTH", "NTL", "NTT", "NVB", "NVL", "NVT", "NWT", "OCB", "OCH", "OIL", "ONE", "ONW", "OPC", "PAI", "PAN", "PBK", "PC1", "PCG", "PCT", "PDB", "PDC", "PDN", "PDR", "PDT", "PDV", "PEG", "PEN", "PEQ", "PET", "PGB", "PGC", "PGD", "PGI", "PGS", "PGT", "PGV", "PHC", "PHP", "PHR", "PIA", "PIC", "PIT", "PIV", "PJC", "PJT", "PLC", "PLX", "PMC", "PME", "PMG", "PNC", "PNG", "PNJ", "POB", "POM", "POS", "POT", "POV", "POW", "POX", "PPC", "PPP", "PPS", "PPT", "PPY", "PQN", "PRC", "PRE", "PSC", "PSD", "PSH", "PSI", "PSN", "PSP", "PTC", "PTD", "PTG", "PTH", "PTI", "PTL", "PTP", "PTS", "PTT", "PTV", "PTX", "PV2", "PVB", "PVC", "PVD", "PVE", "PVG", "PVI", "PVL", "PVM", "PVP", "PVS", "PVT", "PXI", "PXS", "QCG", "QNS", "QPH", "QSP", "QST", "QTC", "QTP", "RBC", "RCD", "RCL", "REE", "RGC", "RIC", "ROS", "RTB", "S4A", "S55", "S99", "SAB", "SAC", "SAF", "SAM", "SAP", "SAS", "SBA", "SBD", "SBH", "SBM", "SBR", "SBT", "SC5", "SCD", "SCI", "SCO", "SCR", "SCS", "SD2", "SD4", "SD5", "SD6", "SD9", "SDT", "SDU", "SEA", "SEB", "SED", "SFC", "SFI", "SGB", "SGC", "SGD", "SGH", "SGI", "SGN", "SGP", "SGR", "SGT", "SHB", "SHE", "SHP", "SHS", "SHX", "SID", "SJ1", "SJC", "SJD", "SJE", "SJS", "SKG", "SLS", "SMB", "SMC", "SMN", "SNC", "SP2", "SPB", "SPD", "SPH", "SPM", "SRA", "SRC", "SRF", "SRT", "SSB", "SSF", "SSG", "SSI", "SSM", "SSN", "ST8", "STB", "STC", "STG", "STH", "STK", "STT", "SUM", "SVH", "SWC", "SZB", "SZC", "SZL", "T12", "TA9", "TAC", "TAR", "TBC", "TBD", "TC6", "TCB", "TCD", "TCH", "TCL", "TCM", "TCO", "TCT", "TCW", "TDB", "TDC", "TDG", "TDH", "TDN", "TDS", "TDT", "TET", "TGP", "TH1", "THB", "THD", "THI", "THM", "THS", "THT", "TIC", "TIG", "TIP", "TIS", "TIX", "TJC", "TKC", "TLH", "TLI", "TMB", "TMC", "TMP", "TMS", "TN1", "TNB", "TNC", "TNG", "TNP", "TNS", "TOP", "TOS", "TOT", "TPB", "TPH", "TPS", "TR1", "TRA", "TRC", "TS4", "TSB", "TSD", "TSJ", "TST", "TTA", "TTE", "TTG", "TTL", "TTN", "TTS", "TTT", "TTZ", "TV2", "TVB", "TVD", "TVN", "TVS", "TVT", "TW3", "TYA", "UDC", "UNI", "UPH", "V12", "V21", "VAB", "VBB", "VC1", "VC2", "VC3", "VC6", "VC7", "VC9", "VCA", "VCB", "VCC", "VCF", "VCG", "VCI", "VCM", "VCP", "VDB", "VDL", "VDM", "VDN", "VDP", "VDS", "VDT", "VE1", "VE2", "VE3", "VE4", "VE8", "VEC", "VEF", "VES", "VFC", "VFG", "VFR", "VGG", "VGI", "VGP", "VGS", "VGT", "VHC", "VHE", "VHG", "VHM", "VIB", "VIC", "VIG", "VIP", "VIR", "VIS", "VIX", "VJC", "VLF", "VMC", "VMD", "VMG", "VMI", "VMS", "VNA", "VNB", "VND", "VNE", "VNF", "VNG", "VNH", "VNL", "VNM", "VNR", "VNS", "VNT", "VNX", "VOS", "VPD", "VPH", "VPI", "VPR", "VRC", "VRE", "VRG", "VSA", "VSC", "VSF", "VSH", "VSI", "VSM", "VSN", "VTC", "VTD", "VTE", "VTG", "VTH", "VTJ", "VTM", "VTO", "VTR", "VXB", "WCS", "WSS", "X20", "X26", "YEG"}

# === Hàm chuẩn hóa ngày đăng ===
def clean_date(date_str):
    try:
        raw = date_str.split(" - ")[0].strip()
        return datetime.strptime(raw, "%d-%m-%Y").strftime("%Y-%m-%d")
    except Exception as e:
        return None

# === Hàm làm sạch văn bản ===
def clean_text(text):
    text = re.sub(r"\s+", " ", text)         # xóa khoảng trắng thừa
    text = re.sub(r"(?<=\w)\.(?=\w)", ". ", text)  # sửa thiếu dấu cách sau dấu chấm
    return text.strip()

# === Hàm trích mã cổ phiếu từ text ===
def extract_tickers(text, ticker_list):
    upper_words = set(re.findall(r"\b[A-Z]{2,5}\b", unidecode(text)))
    return list(upper_words & ticker_list)

# === Load dữ liệu ===
with open(r"cafef_articles\2025-04-11\articles_combined_temp.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# === Tiền xử lý ===
processed = []
for article in articles:
    try:
        combined_text = " ".join([
            article.get("title", ""),
            article.get("sapo", ""),
            article.get("summary", ""),
            article.get("content", "")
        ])

        tickers = extract_tickers(combined_text, vietnam_tickers)

        processed.append({
            "title": clean_text(article.get("title", "")),
            "date": clean_date(article.get("published_time", "")),
            "category": article.get("category", ""),
            "tickers": tickers,
            "summary": clean_text(article.get("summary", "")),
            "sapo": clean_text(article.get("sapo", "")),
            "content": clean_text(article.get("content", ""))
        })
    except Exception as e:
        print("❌ Lỗi xử lý bài:", article.get("link"), e)

# === Lưu kết quả đã xử lý ===
with open("articles_preprocessed.json", "w", encoding="utf-8") as f:
    json.dump(processed, f, ensure_ascii=False, indent=2)

print(f"✅ Đã xử lý {len(processed)} bài viết và lưu vào 'articles_preprocessed.json'")
