// Boys pyramid:  MLS Next > ECNL Boys > USYS National > USYS Youth > ECNL-R/NPL/EDP > State
// Girls pyramid: ECNL Girls > Girls Academy > USYS National > USYS Youth > ECNL-R/NPL/EDP > State

const LEAGUES_M: Record<string, string[]> = {
  'Recreational': ['Recreation League', 'Intramural', 'Other'],
  'Competitive Club': [
    'MLS Next',
    'ECNL Boys',
    'USYS National League',
    'USYS Youth League',
    'ECNL Regional',
    'NPL',
    'EDP',
    'US Club Soccer',
    'State League',
    'State Cup',
    'Regional League',
    'Other',
  ],
  'Academy/Select': [
    'MLS Next',
    'ECNL Boys',
    'USYS National League',
    'USYS Youth League',
    'ECNL Regional',
    'NPL',
    'EDP',
    'US Club Soccer',
    'State League',
    'Other',
  ],
  'Varsity High School': ['High School Varsity', 'State Ranked', 'Other'],
  'College': ['NCAA D1', 'NCAA D2', 'NCAA D3', 'NAIA', 'NJCAA', 'Other'],
  'Professional': ['MLS', 'MLS Next Pro', 'USL Championship', 'USL1', 'USL League Two', 'UPSL', 'Other'],
};

const LEAGUES_W: Record<string, string[]> = {
  'Recreational': ['Recreation League', 'Intramural', 'Other'],
  'Competitive Club': [
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
    'Regional League',
    'Other',
  ],
  'Academy/Select': [
    'ECNL Girls',
    'Girls Academy',
    'USYS National League',
    'USYS Youth League',
    'ECNL Regional',
    'NPL',
    'EDP',
    'US Club Soccer',
    'State League',
    'Other',
  ],
  'Varsity High School': ['High School Varsity', 'State Ranked', 'Other'],
  'College': ['NCAA D1', 'NCAA D2', 'NCAA D3', 'NAIA', 'NJCAA', 'Other'],
  'Professional': ['NWSL', 'USL Super League', 'W League', 'Other'],
};

export function getLeagues(level: string, gender: 'M' | 'W'): string[] {
  const map = gender === 'W' ? LEAGUES_W : LEAGUES_M;
  return map[level] ?? ['Other'];
}

// Legacy export kept for any existing callers
export const LEAGUES_BY_LEVEL = LEAGUES_M;
