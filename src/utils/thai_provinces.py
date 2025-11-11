#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thai Provinces Data and Utilities
================================
ข้อมูลจังหวัดในประเทศไทยสำหรับใช้ในการค้นหาและกรองผลลัพธ์
"""

THAI_PROVINCES = {
    "กรุงเทพมหานคร": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "ห้างสรรพสินค้า", "ตลาด", "สถานที่ท่องเที่ยว"],
        "examples": ["สยามพารากอน", "เซ็นทรัลเวิลด์", "จตุจักร", "วัดพระแก้ว", "เอราวัณด์"],
        "aliases": ["bangkok", "กทม"]
    },
    "เชียงใหม่": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "ตลาดน้ำ", "วัด", "สถานที่ท่องเที่ยว"],
        "examples": ["โดยติเศรษฐี", "ตลาดน้ำตำแยง", "วัดพระธาตุดอยสุเทพ", "นิมมานเฮมต์"],
        "aliases": ["chiang mai"]
    },
    "ภูเก็ต": {
        "region": "th",
        "search_keywords": ["โรงแรม", "หาด", "ร้านอาหาร", "ตลาด", "สถานที่ท่องเที่ยว"],
        "examples": ["หาดป่าตอง", "ถนนบังกะโล", "โรงแรมอันดามัน", "เฟชิวัลเซลล์"],
        "aliases": ["phuket"]
    },
    "สุราษฎร์ธานี": {
        "region": "th",
        "search_keywords": ["โรงแรม", "หาด", "เกาะ", "ร้านอาหาร", "สถานที่ท่องเที่ยว"],
        "examples": ["เกาะสมุย", "เกาะพงัน", "หาดชะอำ", "อ่าวนางเที่ยง"],
        "aliases": ["surat thani"]
    },
    "กระบี่": {
        "region": "th",
        "search_keywords": ["โรงแรม", "หาด", "เกาะ", "ร้านอาหาร", "สถานที่ท่องเที่ยว"],
        "examples": ["เกาะพีพี", "อ่าวมาหำน", "เกาะไต้ตง", "หาดไร่เลย์"],
        "aliases": ["krabi"]
    },
    "ชลบุรี": {
        "region": "th",
        "search_keywords": ["โรงแรม", "หาด", "ร้านอาหาร", "ตลาด", "สถานที่ท่องเที่ยว"],
        "examples": ["พัทยา", "บางแสน", "หาดบางเสน", "ซันไชน์บีช"],
        "aliases": ["chonburi", "pattaya"]
    },
    "นครราชสีมา": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "ห้างสรรพสินค้า", "วัด", "สถานที่ท่องเที่ยว"],
        "examples": ["เดอะมอล", "วัดพระนาค", "อุทยานแห่งชาติเขาใหญ่", "ตลาดมอดิน"],
        "aliases": ["nakhon ratchasima", "korat"]
    },
    "ขอนแก่น": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "ตลาด", "มหาวิทยาลัย", "สถานที่ท่องเที่ยว"],
        "examples": ["มหาวิทยาลัยขอนแก่น", "ตลาดเทศบาล", "วัดท่าศาลา", "อ่างเก็บน้ำห้วยแก้ว"],
        "aliases": ["khon kaen"]
    },
    "เชียงราย": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "วัด", "ตลาด", "สถานที่ท่องเที่ยว"],
        "examples": ["ดอยสุเทพ", "วัดร่องฟอง", "ตลาดหานใหม่", "บ้านดอยเสด็จ"],
        "aliases": ["chiang rai"]
    },
    "หาดใหญ่": {
        "region": "th",
        "search_keywords": ["โรงแรม", "หาด", "ร้านอาหาร", "สถานที่ท่องเที่ยว"],
        "examples": ["หาดใหญ่", "วัดเขาตะเครน", "ตลาดไทย-หลวง", "สวนสมเด็จเจ้าพ่อพระราม 2"],
        "aliases": ["hua hin"]
    },
    "นราธิวาสรรม": {
        "region": "th",
        "search_keywords": ["โรงแรม", "หาด", "ร้านอาหาร", "สถานที่ท่องเที่ยว"],
        "examples": ["วัดพระใหญ่", "หาดวอนนา", "ตลาดศรีเมือง", "อนุสาวรีย์ท้าวศรีสุนทร"],
        "aliases": ["nakhon pathom"]
    },
    "สงขลา": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "ภูเขา", "สถานที่ท่องเที่ยว"],
        "examples": ["เขาคูหาด", "ดอยอ่างขาง", "วัดพระธาตุดอยสุเทพ", "ตลาดสดเมืองสงขลา"],
        "aliases": ["songkhla"]
    },
    "พัทยา": {
        "region": "th",
        "search_keywords": ["โรงแรม", "หาด", "ร้านอาหาร", "ตลาด", "สถานที่ท่องเที่ยว"],
        "examples": ["หาดพัทยา", "เดอะมอล", "วัดใหญ่", "ตลาดตำหนัก"],
        "aliases": ["pattaya"]
    },
    "นครศรีธรรมราช": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "วัด", "ตลาด", "สถานที่ท่องเที่ยว"],
        "examples": ["วัดพระศรีรัตนศาสดิ์", "ตลาดใหญ่", "อ่าวมะนาว", "สวนหลวง"],
        "aliases": ["nakhon si thammarat"]
    },
    "อุบลราชธานี": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "วัด", "ตลาด", "สถานที่ท่องเที่ยว"],
        "examples": ["วัดใหญ่", "ตลาดใหญ่", "พระธาตุอุบล", "สวนสมเด็จเจ้าพ่อพระอุปัณฑาสาร"],
        "aliases": ["ubon ratchathani"]
    }
}

def get_all_provinces():
    """คืนค่ารายชื่อจังหวัดทั้งหมด"""
    return list(THAI_PROVINCES.keys())

def get_province_data(province_name):
    """คืนค่าข้อมูลจังหวัด"""
    # ค้นหาจากชื่อเต็ม
    if province_name in THAI_PROVINCES:
        return THAI_PROVINCES[province_name]

    # ค้นหาจาก aliases
    for province, data in THAI_PROVINCES.items():
        if province_name.lower() in [alias.lower() for alias in data.get('aliases', [])]:
            return data

    return None

def enhance_search_query_with_province(query, province):
    """เพิ่มจังหวัดลงในคำค้นสำหรับการค้นหาที่แม่นยำขึ้น"""
    if not province or not get_province_data(province):
        return query

    # สร้างคำค้นที่มีจังหวัดปนอยู่
    province_variants = [
        f"{query} จังหวัด{province}",
        f"{query} {province}",
        f"{query} ใน{province}",
        f"{query} ที่{province}"
    ]

    return province_variants[0]  # ใช้รูปแบบแรก

def get_province_suggestions(query):
    """คืนค่าคำแนะนำจังหวัดจากคำค้น"""
    suggestions = []
    query_lower = query.lower()

    for province, data in THAI_PROVINCES.items():
        # ตรวจสอบชื่อจังหวัด
        if query_lower in province.lower():
            suggestions.append(province)
            continue

        # ตรวจสอบ aliases
        for alias in data.get('aliases', []):
            if query_lower in alias.lower():
                suggestions.append(province)
                break

    return suggestions[:5]  # คืนค่าสูงสุด 5 อันแรก

def get_popular_search_terms():
    """คืนค่าคำค้นยอดนิยมสำหรับจังหวัดไทย"""
    terms = []
    for province, data in THAI_PROVINCES.items():
        for keyword in data.get('search_keywords', [])[:2]:  # 2 คำแรกต่อจังหวัด
            terms.append({
                'term': keyword,
                'province': province,
                'full_query': f"{keyword} จังหวัด{province}"
            })

    return terms[:20]  # คืนค่าสูงสุด 20 รายการ

def validate_province_search(query, province):
    """ตรวจสอบความถูกต้องของการค้นหาตามจังหวัด"""
    if not query:
        return False, "กรุณาระบุคำค้น"

    if not province:
        return True, "ค้นหาทั่วประเทศไทย"

    if not get_province_data(province):
        return False, f"จังหวัด '{province}' ไม่พบในระบบ"

    return True, f"ค้นหาในจังหวัด{province}"