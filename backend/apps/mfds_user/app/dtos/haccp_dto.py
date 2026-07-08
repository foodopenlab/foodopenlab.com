from dataclasses import dataclass, field
from typing import Optional, List

@dataclass(frozen=True)
class HaccpProductInfoDTO:
    found: bool
    prdlst_report_no: str
    product_name: Optional[str] = None
    manufacturer: Optional[str] = None
    raw_materials: List[str] = field(default_factory=list)
    allergens: List[str] = field(default_factory=list)
    nutrient_info: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    barcode: Optional[str] = None
