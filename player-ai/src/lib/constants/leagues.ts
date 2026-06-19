// Single source of truth for league options shown in onboarding and profile edit.
// Boys pyramid:  MLS Next > ECNL Boys > USYS National > USYS Youth > ECNL-R/NPL/EDP > USYS State / US Club
// Girls pyramid: ECNL Girls > Girls Academy > USYS National > USYS Youth > ECNL-R/NPL/EDP > USYS State / US Club
// Both lists merged so players self-select regardless of gender.

export const LEAGUES_BY_LEVEL: Record<string, string[]> = {
  'Recreational': [
    'Recreation League',
    'Intramural',
    'Other',
  ],
  'Competitive Club': [
    // Tier 1 boys / girls
    'MLS Next',
    'ECNL Boys',
    'ECNL Girls',
    'Girls Academy',
    // Tier 3
    'USYS National League',
    'USYS Youth League',
    // Tier 4
    'ECNL Regional',
    'NPL',
    'EDP',
    // Tier 5
    'US Club Soccer',
    'State League',
    'State Cup',
    'Regional League',
    'Other',
  ],
  'Academy/Select': [
    'MLS Next',
    'ECNL Boys',
    'ECNL Girls',
    'Girls Academy',
    'USYS National League',
    'USYS Youth League',
    'ECNL Regional',
    'NPL',
    'EDP',
    'US Club Soccer',
    'State League',
    'State Cup',
    'Other',
  ],
  'Varsity High School': [
    'High School Varsity',
    'State Ranked',
    'Other',
  ],
  'College': [
    'NCAA D1',
    'NCAA D2',
    'NCAA D3',
    'NAIA',
    'NJCAA',
    'Other',
  ],
  'Professional': [
    'MLS',
    'MLS Next Pro',
    'USL Championship',
    'USL Super League',
    'USL1',
    'USL League Two',
    'UPSL',
    'Other',
  ],
};
