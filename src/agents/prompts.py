SUMMARY_PROMPT = """
Provide a 2-sentence summary of the key announcements or policy changes from this finance speech transcript.
Output ONLY a JSON object:
{{
  "summary": "Your summary here"
}}

Transcript:
{full_transcript}
"""

TOPICS_PROMPT = """
Identify ONLY the main topics explicitly discussed in the following summary of a finance speech.
Output ONLY a JSON object:
{{
  "topics": [
    {{"topic": "topic name", "details": "brief details"}}
  ]
}}

Summary:
{combined_summary}
"""

IMPACT_PROMPT = """
Based on this summary of a finance speech, provide a concise market sentiment analysis.
Output ONLY a JSON object:
{{
  "market_impact": "One sentence: Bullish/Neutral/Bearish and the primary reason."
}}

Summary:
{combined_summary}
"""

SECTORS_PROMPT = """
Based on this summary of a finance speech, analyze ONLY the sectors that are DIRECTLY MENTIONED or IMPACTED.
Do NOT list sectors that are not discussed.
Output ONLY a JSON object with this structure (max 15 words per reason):
{{
  "sector_impacts": {{
    "Sector Name": {{"impact": "Positive/Negative/Neutral", "reason": "concise reason"}}
  }}
}}

Summary:
{combined_summary}
"""

COMBINED_ANALYSIS_PROMPT = """
You are a professional financial analyst AI with deep knowledge of the Indian stock market (NSE/BSE). Your task is to analyze summarized content from a Finance Minister's speech (typically Union Budget or Finance Bill related) and produce a structured, objective assessment.

When identifying sector impacts, you MUST ONLY use sector names exactly as they appear in the following official list from Screener.in (do not create, combine, rename, or invent new sector names):

2/3 Wheelers, Abrasives & Bearings, Advertising & Media Agencies, Aerospace & Defense, Airline, Airport & Airport services, Aluminium, Aluminium, Copper & Zinc Products, Amusement Parks/ Other Recreation, Animal Feed, Asset Management Company, Auto Components & Equipments, Auto Dealer, Biotechnology, Breweries & Distilleries, Business Process Outsourcing (BPO)/ Knowledge Process Outsourcing (KPO), Cables - Electricals, Carbon Black, Castings & Forgings, Cement & Cement Products, Ceramics, Cigarettes & Tobacco Products, Civil Construction, Coal, Commercial Vehicles, Commodity Chemicals, Compressors, Pumps & Diesel Engines, Computers - Software & Consulting, Computers Hardware & Equipments, Construction Vehicles, Consulting Services, Consumer Electronics, Copper, Dairy Products, Data Processing Services, Dealers-Commercial Vehicles, Tractors, Construction Vehicles, Depositories, Clearing Houses and Other Intermediaries, Digital Entertainment, Distributors, Diversified, Diversified Commercial Services, Diversified consumer products, Diversified FMCG, Diversified Metals, Diversified Retail, Dredging, Dyes And Pigments, E-Learning, E-Retail/ E-Commerce, Edible Oil, Education, Electrodes & Refractories, Electronic Media, Exchange and Data Platform, Explosives, Ferro & Silica Manganese, Fertilizers, Film Production, Distribution & Exhibition, Financial Institution, Financial Products Distributor, Financial Technology (Fintech), Footwear, Forest Products, Furniture, Home Furnishing, Garments & Apparels, Gas Transmission/Marketing, Gems, Jewellery And Watches, General Insurance, Glass - Consumer, Glass - Industrial, Granites & Marbles, Healthcare Research, Analytics & Technology, Healthcare Service Provider, Heavy Electrical Equipment, Holding Company, Hospital, Hotels & Resorts, Household Appliances, Household Products, Houseware, Housing Finance Company, Industrial Gases, Industrial Minerals, Industrial Products, Insurance Distributors, Integrated Power Utilities, Internet & Catalogue Retail, Investment Company, Iron & Steel, Iron & Steel Products, IT Enabled Services, Jute & Jute Products, Leather And Leather Products, Leisure Products, Life Insurance, Logistics Solution Provider, LPG/CNG/PNG/LNG Supplier, Lubricants, Meat Products including Poultry, Media & Entertainment, Medical Equipment & Supplies, Microfinance Institutions, Multi Utilities, Non Banking Financial Company (NBFC), Offshore Support Solution Drilling, Oil Equipment & Services, Oil Exploration & Production, Oil Storage & Transportation, Other Agricultural Products, Other Bank, Other Beverages, Other Construction Materials, Other Consumer Services, Other Electrical Equipment, Other Financial Services, Other Food Products, Other Industrial Products, Other Telecom Services, Other Textile Products, Packaged Foods, Packaging, Paints, Paper & Paper Products, Passenger Cars & Utility Vehicles, Personal Care, Pesticides & Agrochemicals, Petrochemicals, Pharmaceuticals, Pharmacy Retail, Pig Iron, Plastic Products - Consumer, Plastic Products - Industrial, Plywood Boards/ Laminates, Port & Port services, Power - Transmission, Power Distribution, Power Generation, Power Trading, Precious Metals, Print Media, Printing & Publication, Printing Inks, Private Sector Bank, Public Sector Bank, Railway Wagons, Ratings, Real Estate Investment Trusts (REITs), Refineries & Marketing, Residential, Commercial Projects, Restaurants, Road Assets Toll, Annuity, Hybrid-Annuity, Road Transport, Rubber, Sanitary Ware, Seafood, Ship Building & Allied Services, Shipping, Software Products, Speciality Retail, Specialty Chemicals, Sponge Iron, Stationary, Stockbroking & Allied, Sugar, Tea & Coffee, Telecom - Equipment & Accessories, Telecom - Cellular & Fixed line services, Telecom - Infrastructure, Tractors, Trading - Auto components, Trading - Chemicals, Trading - Gas, Trading - Metals, Trading - Minerals, Trading - Textile Products, Trading & Distributors, TV Broadcasting & Software Production, Tyres & Rubber Products, Waste Management, Water Supply & Management, Web based media and service, Wellness, Zinc

Strict rules:
1. Only include a sector in "sector_impacts" if the speech summary contains explicit, direct references or measures that clearly affect that exact sector (tax change, subsidy, duty, regulation, allocation, incentive, ban, etc.).
2. Do NOT infer indirect or second-order effects unless explicitly stated in the summary.
3. If no direct impact is mentioned for a sector, do NOT include it in the output — leave the sector_impacts object empty or only with clearly affected sectors.
4. Use “Unknown” only when the summary is ambiguous about sentiment or impact direction despite mentioning the topic/sector.
5. Be extremely conservative and factual — avoid speculation.



CRITICAL: You MUST output ONLY a valid JSON object. Do NOT include:
- Markdown code blocks (no ```json or ```)
- Any explanatory text before or after the JSON
- Any comments or additional formatting

Output format requirements:
1. Start your response with {{ (opening brace)
2. End your response with }} (closing brace)
3. Use proper JSON syntax with double quotes for all keys and string values
4. Ensure all nested objects and arrays are properly formatted

Expected JSON structure:

{{
  "topics": [
    {{"topic": "topic name", "details": "brief detail"}}
  ],
  "market_impact": {{
    "sentiment": "Bullish/Neutral/Bearish",
    "reason": "concise primary reason (max 20 words)"
  }},
  "sector_impacts": {{
    "SectorName1": {{"impact": "Positive/Negative/Neutral", "reason": "concise reason (max 15 words)"}},
    "SectorName2": {{"impact": "Positive/Negative/Neutral", "reason": "concise reason (max 15 words)"}}
  }}
}}

Local Summary: {local_summary}

Full Transcript: {transcript}

Remember: Output ONLY the JSON object, nothing else.
"""



