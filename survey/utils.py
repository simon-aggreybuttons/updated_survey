from __future__ import annotations

import re

from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> str:
    """Try to extract the client IP from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def get_user_agent(request: HttpRequest) -> str:
    """Return the browser user-agent header."""
    return request.META.get('HTTP_USER_AGENT', '')[:200]


def get_sector_company_label(sector: str | None) -> str:
    if not sector:
        return 'the selected companies'

    labels = {
        'Banking': 'banks',
        'Utilities': 'utility companies',
        'Telecommunications': 'telecom providers',
        'Hospitality': 'hotels',
        'Healthcare': 'healthcare providers',
        'Retail Malls': 'retail malls',
        'Public Institutions': 'public institutions',
        'Online Businesses': 'online businesses',
        'Transportation': 'transport providers',
        'Insurance': 'insurance companies',
        'Oil Marketing Companies': 'oil marketing companies',
    }
    return labels.get(sector, 'organizations')


def get_sector_company_singular_label(sector: str | None) -> str:
    if not sector:
        return 'company'

    labels = {
        'Banking': 'bank',
        'Utilities': 'utility company',
        'Telecommunications': 'telecommunication company',
        'Hospitality': 'hotel',
        'Healthcare': 'healthcare provider',
        'Retail Malls': 'retail mall',
        'Public Institutions': 'public institution',
        'Online Businesses': 'online business',
        'Transportation': 'transport provider',
        'Insurance': 'insurance company',
        'Oil Marketing Companies': 'oil marketing company',
    }
    return labels.get(sector, 'company')


def get_sector_companies(sector: str | None) -> list[str]:
    companies = {
        'Banking': [
            'Absa Bank Ghana Limited',
            'Access Bank (Ghana) Plc',
            'Agricultural Development Bank Limited',
            'Bank of Africa Ghana Limited',
            'CAL Bank Limited',
            'Consolidated Bank Ghana Limited',
            'Ecobank Ghana Limited',
            'FBNBank (Ghana) Limited',
            'Fidelity Bank Ghana Limited',
            'First Atlantic Bank Limited',
            'First National Bank (Ghana) Limited',
            'GCB Bank Limited',
            'GHL Bank Limited',
            'Guaranty Trust Bank (Ghana) Limited',
            'National Investment Bank Limited',
            'OmniBSIC Bank Ghana Limited',
            'Prudential Bank Limited',
            'Republic Bank (Ghana) Limited',
            'Societe Generale (Ghana) Limited',
            'Stanbic Bank Ghana Limited',
            'Standard Chartered Bank (Ghana) Limited',
            'United Bank for Africa (Ghana) Limited',
            'Universal Merchant Bank Limited',
            'Zenith Bank (Ghana) Limited',
        ],
        'Utilities': [
            'Electricity Company of Ghana',
            'Ghana Water Company',
            'Zoomlion Ghana Limited',
        ],
        'Telecommunications': [
            'AirtelTigo',
            'Busy Internet',
            'MTN',
            'Surfline',
            'Teledata ICT',
            'Telecel',
            'Zipnet',
        ],
        'Hospitality': [
            'Accra City Hotel',
            'Accra Marriot Hotel',
            'Aiport West Hotel',
            'Airport View Hotel',
            'Aqua Safari',
            'Best Western Premier Accra Airport Hotel',
            'Fiesta Royale Hotel',
            'Golden Tulip Accra',
            'Golden Tulip Kumasi City',
            'Holiday Inn Aiport Accra',
            'Ibis Styles Accra Airport City',
            'Kempinski Hotel Gold Coast City',
            'La Palm Royal Beach Hotel',
            'Labadi Beach Hotel',
            'Movenpick Ambassador Hotel Accra',
            'Safari Valley',
            'Swiss Spirit Alisa Hotels North Ridge',
            'The African Regent Hotel',
            'The Royal Senchi',
        ],
        'Healthcare': [
            '37 Military Hospital',
            'Accra Psychiatric Hospital',
            'Achimota Hospital',
            'Aiport Womens Hospital',
            'Del International Hospital',
            'Dodowa District Hospital',
            'Family Health Hospital',
            'Greater Accra Regional Hospital (Ridge Hospital)',
            'Komfo Anokye Teaching Hospital',
            'Korle-Bu Teaching Hospital',
            'Lapaz Community Hospital',
            'LEKMA Hospital',
            'Lister Hospital and Fertility Centre',
            'Nyaho Hospital',
            'Rabito Hospital',
            'St. John\'s Hospital and Fertility Centre',
            'Sunyani Regional Hospital',
            'Tamale Teaching Hospital',
            'University of Ghana Medical Center (UGMC)',
            'Volta Regional Hospital',
        ],
        'Retail Malls': [
            'A&C Mall',
            'Accra Mall',
            'Achimota Retail Centre',
            # 'CityDia' removed (does not exist)
            'Junction Mall',
            'Koala Shopping Mall',
            'Kumasi City Mall',
            'Marina Mall',
            'Max Mart',
            'Melcom',
            'Orca Deco',
            'Oxford Street Mall',
            'Palace Shopping Centre',
            'Takoradi Mall',
            'West Hills Mall',
        ],
        'Public Institutions': [
            'Driver and Vehicle Licensing Authority (DVLA)',
            'Food and Drugs Authority',
            'Ghana Broadcasting Corporation',
            'Ghana Civil Aviation Authority',
            'Ghana Free Zones Board',
            'Ghana Investment Promotion Centre',
            'Ghana Police Service',
            'Ghana Revenue Authority',
            'Ghana Shippers Authority',
            'Ghana Standards Authority',
            'Social Security and National Insurance Trust (SSNIT)',
        ],
        'Online Businesses': [
            'Afrikart',
            'Alibaba Online Shopping Site',
            'Baahe.com',
            'Deus.com.gh',
            'Hubtel Mall',
            'Jumia',
            'Melcome Ghana Online Shopping',
            'Tonaton.com',
            'Zoobashop',
        ],
        'Transportation': [
            'Accra Cab',
            'Bolt',
            # 'Dropyn' removed
            # 'Poki Cab' removed
            'Uber',
            'Yango',
        ],
        'Insurance': [
            'Acacia',
            'Activa International Insurance Company-Ghana Limited',
            'Allianz Insurance Company Gh. Ltd.',
            'Donewell Insurance Company Limited',
            'Enterprise Insurance Company Limited',
            'Enterprise Life',
            'Glico',
            'GN Life Assurance Limited',
            'Hollard Insurance Ghana Limited',
            'Hollard Life',
            'Imperial General Insurance Company Ltd.',
            'Metropolitan Life Insurance Ghana Limited',
            'NSIA Insurance Company Limited',
            'Provident Insurance Company Limited',
            'Prudential Life Insurance Ghana',
            'Regency Nem Insurance Ghana Limited',
            'SIC Insurance Company Limited',
            'Star Assurance Company Limited',
            'Starlife Assurance Company Limited',
            'Vanguard Assurance Company Limited',
        ],
        'Oil Marketing Companies': [
            'Allied',
            'Frimps',
            'Goil',
            'Gulf Energy',
            'Puma',
            'Sel',
            'Shell',
            'Star Oil',
            'Total',
            'Unity Oil',
        ],
    }
    return companies.get(sector, [])


def render_question_text(text: str, sector: str | None = None, company: str | None = None) -> str:
    if not text:
        return text

    safe_sector = sector or 'selected sector'
    safe_company = company or 'your selected company'
    replacements = {
        'BANKING_SECTOR': safe_sector,
        'ALL_THE_BANKS': get_sector_company_label(sector),
        'ALL_THE_COMPANIES': get_sector_company_label(sector),
        'COMPANY_TYPE': get_sector_company_label(sector),
        'COMPANY_TYPE_SINGULAR': get_sector_company_singular_label(sector),
        'SELECTED_COMPANY': safe_company,
        'COMPANY': safe_company,
        'SELECTED_SECTOR': safe_sector,
    }
    for placeholder, replacement in replacements.items():
        text = text.replace(placeholder, replacement)

    text = re.sub(r'\bBANKING_SECTOR\b', safe_sector, text, flags=re.IGNORECASE)
    text = re.sub(r'\bBANKS\b', get_sector_company_label(sector), text, flags=re.IGNORECASE)
    text = re.sub(r'\bBANK\b', get_sector_company_singular_label(sector), text, flags=re.IGNORECASE)
    return text
