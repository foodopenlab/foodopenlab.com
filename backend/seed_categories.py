import sys
import asyncio
from pathlib import Path

# Setup paths
_BACKEND_DIR = Path("c:/Users/hi/Documents/com.foodopenlab/com.auditor")
sys.path.insert(0, str(_BACKEND_DIR))
sys.path.insert(0, str(_BACKEND_DIR / "core"))
sys.path.insert(0, str(_BACKEND_DIR / "apps"))

from matrix.grid_oracle_database_manager import engine
from sqlalchemy import text
import uuid

# Seeding Data
MEDIA_CATEGORIES = [
    ("media_meat",        "육가공",          "S2N5",       ["햄", "소시지", "육가공", "돈육", "베이컨"]),
    ("media_dairy",       "유가공",          "S2N10",      ["우유", "치즈", "버터", "유가공", "낙농"]),
    ("media_beverage",    "음료·주류",       "S2N6",       ["음료", "주류", "두유", "맥주", "소주"]),
    ("media_bakery",      "제과·베이커리",   "S2N12",      ["빵", "케이크", "과자", "베이커리"]),
    ("media_ramen",       "라면·면류",       "S2N15",      ["라면", "면류", "국수", "파스타"]),
    ("media_sauce",       "간편식·소스",     "S2N16",      ["간편식", "소스", "즉석", "HMR"]),
    ("media_additive",    "소재·첨가물",     "S2N4",       ["첨가물", "소재", "보존료", "당류"]),
    ("media_fermented",   "전통·발효식품",   "S2N13",      ["장류", "김치", "발효", "된장"]),
    ("media_agri",        "농수산·펫푸드",   "S2N3",       ["농산물", "수산물", "펫푸드"]),
    ("media_foodservice", "외식·프랜차이즈", "S2N7",       ["외식", "프랜차이즈", "급식"]),
    ("media_distribution","급식·유통",       "S2N9",       ["유통", "급식", "물류"]),
    ("media_packaging",   "포장·기계",       "S2N18",      ["포장", "기계", "용기"]),
    ("media_health",      "건기식",          "S2N2",       ["건강기능식품", "건기식", "홍삼"]),
    ("media_foodtech",    "푸드테크",        "S2N1",       ["푸드테크", "대체육", "배양육"]),
    ("media_esg",         "ESG",             "S2N19",      ["ESG", "친환경", "탄소중립"]),
    # 식품저널·푸드아이콘은 선택 UI 제외 — CompositeNewsAdapter가 항상 크롤링
]

FOODTYPE_PARENT_CATEGORIES = [
    ("ft_confectionery", "과자류·빵류·떡류",      False, ["과자", "빵", "떡", "케이크", "쿠키"]),
    ("ft_ice",           "빙과류",                False, ["아이스크림", "빙과", "샤베트"]),
    ("ft_chocolate",     "코코아·초콜릿류",       False, ["초콜릿", "코코아", "초콜릿가공품"]),
    ("ft_sugar",         "당류",                  False, ["설탕", "시럽", "올리고당", "물엿", "과당"]),
    ("ft_jam",           "잼류",                  False, ["잼", "마멀레이드"]),
    ("ft_soy",           "두부류·묵류",           False, ["두부", "묵", "유바", "가공두부"]),
    ("ft_oil",           "식용유지류",            False, ["식용유", "참기름", "들기름", "마가린", "쇼트닝"]),
    ("ft_noodle",        "면류",                  False, ["라면", "국수", "파스타", "당면", "생면"]),
    ("ft_beverage",      "음료류",                False, ["음료", "탄산", "주스", "두유", "차", "커피"]),
    ("ft_infant",        "특수영양식품",           True,  ["분유", "이유식", "조제유", "성장기조제식", "임산부식품"]),
    ("ft_medical",       "특수의료용도식품",       True,  ["환자식", "영양조제식품", "당뇨환자식", "연하곤란식"]),
    ("ft_fermented_soy", "장류",                  False, ["된장", "간장", "고추장", "청국장", "메주"]),
    ("ft_seasoning",     "조미식품",              False, ["소스", "케첩", "마요네즈", "식초", "카레", "향신료", "식염"]),
    ("ft_pickle",        "절임류·조림류·김치류",  False, ["김치", "장아찌", "피클", "절임", "조림"]),
    ("ft_liquor",        "주류",                  False, ["맥주", "소주", "와인", "막걸리", "위스키"]),
    ("ft_agri",          "농산가공식품류",         False, ["전분", "밀가루", "쌀", "시리얼", "견과류"]),
    ("ft_meat",          "식육가공품류·포장육",   False, ["햄", "소시지", "베이컨", "양념육", "포장육"]),
    ("ft_egg",           "알가공품류",             True,  ["달걀", "계란", "전란액", "난황", "알가공품"]),
    ("ft_dairy",         "유가공품류",            False, ["우유", "치즈", "버터", "발효유", "요거트", "분유"]),
    ("ft_fish",          "수산가공식품류",         False, ["어묵", "젓갈", "건어물", "어육소시지", "액젓"]),
    ("ft_animal",        "동물성가공식품류",       False, ["곤충가공", "자라", "기타동물성가공"]),
    ("ft_honey",         "벌꿀·화분가공품류",     True,  ["벌꿀", "꿀", "로열젤리", "화분", "프로폴리스"]),
    ("ft_instant",       "즉석식품류",            False, ["즉석밥", "HMR", "레토르트", "밀키트", "만두"]),
    ("ft_etc",           "기타식품류",            False, ["기타가공품", "효소식품"]),
    ("ft_health",        "건강기능식품",           False, ["홍삼", "비타민", "프로바이오틱스", "오메가3", "건강기능식품"]),
]

FOODTYPE_CHILD_CATEGORIES = [
    # 1. 과자류·빵류·떡류
    ("ft_confectionery_snack",  "ft_confectionery", "과자·캔디류",  ["과자", "캔디", "추잉껌"]),
    ("ft_confectionery_bread",  "ft_confectionery", "빵류",         ["빵", "케이크", "쿠키"]),
    ("ft_confectionery_rice",   "ft_confectionery", "떡류",         ["떡", "떡볶이떡", "인절미"]),

    # 2. 빙과류
    ("ft_ice_cream",    "ft_ice", "아이스크림류",  ["아이스크림", "저지방아이스크림", "아이스밀크"]),
    ("ft_ice_mix",      "ft_ice", "아이스크림믹스류", ["아이스크림믹스"]),
    ("ft_ice_other",    "ft_ice", "빙과·얼음류",  ["빙과", "샤베트", "식용얼음"]),

    # 3. 코코아·초콜릿류
    ("ft_chocolate_cocoa", "ft_chocolate", "코코아가공품류", ["코코아매스", "코코아버터", "코코아분말"]),
    ("ft_chocolate_choco", "ft_chocolate", "초콜릿류",       ["초콜릿", "밀크초콜릿", "화이트초콜릿", "준초콜릿"]),

    # 4. 당류
    ("ft_sugar_sugar",   "ft_sugar", "설탕류",    ["설탕", "기타설탕"]),
    ("ft_sugar_oligo",   "ft_sugar", "올리고당류", ["올리고당", "올리고당가공품"]),
    ("ft_sugar_syrup",   "ft_sugar", "당시럽·엿류",["물엿", "덱스트린", "과당"]),

    # 5. 잼류
    ("ft_jam_jam",  "ft_jam", "잼",  ["잼", "기타잼"]),

    # 6. 두부류·묵류
    ("ft_soy_tofu", "ft_soy", "두부류", ["두부", "유바", "가공두부"]),
    ("ft_soy_muk",  "ft_soy", "묵류",   ["묵", "도토리묵", "청포묵"]),

    # 7. 식용유지류
    ("ft_oil_plant",   "ft_oil", "식물성유지류",  ["콩기름", "올리브유", "참기름", "들기름", "채종유"]),
    ("ft_oil_animal",  "ft_oil", "동물성유지류",  ["식용우지", "식용돈지", "어유"]),
    ("ft_oil_process", "ft_oil", "식용유지가공품",["혼합식용유", "마가린", "쇼트닝", "식물성크림"]),

    # 8. 면류
    ("ft_noodle_fresh", "ft_noodle", "생면·숙면",  ["생면", "숙면"]),
    ("ft_noodle_dry",   "ft_noodle", "건면",        ["건면", "국수", "파스타"]),
    ("ft_noodle_fried", "ft_noodle", "유탕면",      ["라면", "유탕면"]),

    # 9. 음료류
    ("ft_beverage_carbonate", "ft_beverage", "탄산음료류",  ["탄산음료", "탄산수"]),
    ("ft_beverage_tea",       "ft_beverage", "다류",         ["침출차", "액상차", "고형차", "녹차", "홍차"]),
    ("ft_beverage_fruit",     "ft_beverage", "과채음료류",   ["과채주스", "농축과채즙", "과채음료"]),
    ("ft_beverage_fermented", "ft_beverage", "발효음료류",   ["유산균음료", "효모음료", "기타발효음료"]),
    ("ft_beverage_soymilk",   "ft_beverage", "두유류",       ["두유", "원액두유", "가공두유"]),
    ("ft_beverage_coffee",    "ft_beverage", "커피류",       ["원두", "인스턴트커피", "커피믹스", "액상커피"]),
    ("ft_beverage_other",     "ft_beverage", "기타음료",     ["혼합음료", "음료베이스", "이온음료"]),

    # 12. 장류
    ("ft_fermented_soy_soy",    "ft_fermented_soy", "간장류",  ["한식간장", "양조간장", "혼합간장"]),
    ("ft_fermented_soy_paste",  "ft_fermented_soy", "된장·고추장류", ["된장", "고추장", "춘장"]),
    ("ft_fermented_soy_other",  "ft_fermented_soy", "청국장·혼합장", ["청국장", "혼합장", "기타장류"]),

    # 13. 조미식품
    ("ft_seasoning_sauce",   "ft_seasoning", "소스류",         ["소스", "마요네즈", "케첩", "복합조미식품"]),
    ("ft_seasoning_vinegar", "ft_seasoning", "식초류",         ["발효식초", "희석초산"]),
    ("ft_seasoning_spice",   "ft_seasoning", "향신료·고춧가루",["고춧가루", "카레", "천연향신료", "후추"]),
    ("ft_seasoning_salt",    "ft_seasoning", "식염류",         ["천일염", "정제소금", "가공소금"]),

    # 14. 절임류·조림류·김치류
    ("ft_pickle_kimchi", "ft_pickle", "김치류",  ["김치", "깍두기", "총각김치", "김칫속"]),
    ("ft_pickle_pickle", "ft_pickle", "절임류",  ["절임식품", "당절임", "장아찌", "피클"]),
    ("ft_pickle_jorim",  "ft_pickle", "조림류",  ["조림"]),

    # 15. 주류
    ("ft_liquor_fermented",  "ft_liquor", "발효주류",  ["탁주", "막걸리", "약주", "청주", "맥주", "과실주"]),
    ("ft_liquor_distilled",  "ft_liquor", "증류주류",  ["소주", "위스키", "브랜디", "리큐르"]),
    ("ft_liquor_other",      "ft_liquor", "기타주류",  ["기타주류", "주정"]),

    # 16. 농산가공식품류
    ("ft_agri_starch",  "ft_agri", "전분·밀가루류",    ["전분", "밀가루", "영양강화밀가루"]),
    ("ft_agri_cereal",  "ft_agri", "시리얼·곡류가공",  ["시리얼", "쌀가공품", "곡류가공품"]),
    ("ft_agri_nut",     "ft_agri", "견과·과채가공품",  ["땅콩버터", "견과류가공품", "과채가공품", "건과"]),

    # 17. 식육가공품류·포장육
    ("ft_meat_ham",      "ft_meat", "햄류",      ["햄", "생햄", "프레스햄"]),
    ("ft_meat_sausage",  "ft_meat", "소시지류",  ["소시지", "발효소시지", "혼합소시지"]),
    ("ft_meat_양념",     "ft_meat", "양념육·포장육", ["양념육", "분쇄가공육", "포장육", "갈비가공품", "베이컨"]),

    # 19. 유가공품류
    ("ft_dairy_milk",     "ft_dairy", "우유·가공유류",  ["우유", "강화우유", "유산균첨가우유", "가공유"]),
    ("ft_dairy_fermented","ft_dairy", "발효유류",       ["발효유", "요거트", "농후발효유", "크림발효유"]),
    ("ft_dairy_cheese",   "ft_dairy", "치즈·버터류",    ["치즈", "가공치즈", "버터", "가공버터"]),
    ("ft_dairy_powder",   "ft_dairy", "분유·농축유류",  ["전지분유", "탈지분유", "가당연유", "유청"]),

    # 20. 수산가공식품류
    ("ft_fish_paste",   "ft_fish", "어육가공품류", ["어묵", "어육소시지", "연육", "어육살"]),
    ("ft_fish_salted",  "ft_fish", "젓갈류",       ["젓갈", "양념젓갈", "액젓", "조미액젓"]),
    ("ft_fish_dried",   "ft_fish", "건포·기타",    ["건어포", "조미건어포", "조미김", "한천"]),

    # 21. 동물성가공식품류
    ("ft_animal_insect", "ft_animal", "곤충가공식품",     ["곤충가공식품", "식용곤충"]),
    ("ft_animal_other",  "ft_animal", "기타동물성가공품", ["자라가공식품", "기타식육", "기타동물성"]),

    # 23. 즉석식품류
    ("ft_instant_ready",  "ft_instant", "즉석섭취·편의식품", ["즉석섭취식품", "신선편의식품", "간편조리세트"]),
    ("ft_instant_cook",   "ft_instant", "즉석조리식품",      ["즉석조리식품", "레토르트", "즉석밥", "HMR", "밀키트"]),
    ("ft_instant_mandu",  "ft_instant", "만두류",            ["만두", "만두피"]),

    # 24. 기타식품류
    ("ft_etc_enzyme",  "ft_etc", "효소식품",  ["효소식품"]),
    ("ft_etc_other",   "ft_etc", "기타가공품",["기타가공품"]),

    # 25. 건강기능식품
    ("ft_health_recognized", "ft_health", "개별인정형",  ["개별인정형원료", "기능성원료"]),
    ("ft_health_listed",     "ft_health", "고시형",      ["홍삼", "비타민", "프로바이오틱스", "오메가3", "루테인", "콜라겐"]),
    ("ft_health_other",      "ft_health", "기타건기식",  ["EPA", "DHA", "식이섬유", "칼슘", "마그네슘"]),
]

async def seed():
    if engine is None:
        print("Engine is None")
        return
        
    async with engine.begin() as conn:
        print("Truncating existing categories...")
        await conn.execute(text("TRUNCATE TABLE industry_category CASCADE"))
        
        # 1. Insert Media Categories
        for code, name, param, keywords in MEDIA_CATEGORIES:
            print(f"Seeding media category {code}...")
            await conn.execute(text(
                "INSERT INTO industry_category (code, type, parent_code, depth, is_flat, name_ko, crawler_param, created_at) "
                "VALUES (:code, 'media', NULL, 1, false, :name, :param, NOW())"
            ), {"code": code, "name": name, "param": param})
            
            # Keywords
            for kw in keywords:
                await conn.execute(text(
                    "INSERT INTO category_keywords (id, category_code, keyword) VALUES (:id, :code, :kw)"
                ), {"id": uuid.uuid4(), "code": code, "kw": kw})
                
        # 2. Insert Foodtype Parent Categories
        for code, name, is_flat, keywords in FOODTYPE_PARENT_CATEGORIES:
            print(f"Seeding foodtype parent category {code}...")
            await conn.execute(text(
                "INSERT INTO industry_category (code, type, parent_code, depth, is_flat, name_ko, crawler_param, created_at) "
                "VALUES (:code, 'foodtype', NULL, 1, :is_flat, :name, NULL, NOW())"
            ), {"code": code, "is_flat": is_flat, "name": name})
            
            # Keywords
            for kw in keywords:
                await conn.execute(text(
                    "INSERT INTO category_keywords (id, category_code, keyword) VALUES (:id, :code, :kw)"
                ), {"id": uuid.uuid4(), "code": code, "kw": kw})
                
        # 3. Insert Foodtype Child Categories
        for code, parent, name, keywords in FOODTYPE_CHILD_CATEGORIES:
            print(f"Seeding foodtype child category {code}...")
            await conn.execute(text(
                "INSERT INTO industry_category (code, type, parent_code, depth, is_flat, name_ko, crawler_param, created_at) "
                "VALUES (:code, 'foodtype', :parent, 2, false, :name, NULL, NOW())"
            ), {"code": code, "parent": parent, "name": name})
            
            # Keywords
            for kw in keywords:
                await conn.execute(text(
                    "INSERT INTO category_keywords (id, category_code, keyword) VALUES (:id, :code, :kw)"
                ), {"id": uuid.uuid4(), "code": code, "kw": kw})
                
    print("Seeding finished successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
