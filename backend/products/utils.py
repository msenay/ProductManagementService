import xml.etree.ElementTree as ET
from typing import Optional


def get_text(element: Optional[ET.Element], default: Optional[str]) -> Optional[str]:
    return element.text if element is not None and element.text is not None else default

def get_float_text(element: Optional[ET.Element], default: Optional[float]) -> Optional[float]:
    return float(element.text.split()[0]) if element is not None and element.text else default

def get_attribute(element: Optional[ET.Element], attribute: str, default: Optional[str] = None) -> Optional[str]:
    return element.attrib.get(attribute, default) if element is not None else default

