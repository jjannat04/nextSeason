import {describe,it,expect} from 'vitest';
import {assertMode,initialComparisonSelection} from './types';
import type {PlanResult} from './types';

describe('response mode boundary',()=>{
  it('blocks fixture output from real prototype rotation options',()=>{
    const response={mode:'prototype_recommendation',status:'rotation_options',dataset_origin:'RESEARCH_EVIDENCE',notice:'DEVELOPMENT_FIXTURE',is_recommendation:true} as unknown as PlanResult;
    expect(()=>assertMode(response,'prototype_recommendation')).toThrow();
  });
  it('requires a real research origin for prototype results',()=>{
    expect(()=>assertMode({mode:'prototype_recommendation'} as PlanResult,'prototype_recommendation')).toThrow();
    expect(()=>assertMode({mode:'prototype_recommendation',dataset_origin:'RESEARCH_EVIDENCE'} as unknown as PlanResult,'prototype_recommendation')).not.toThrow();
  });
  it('blocks fixture output in the production view',()=>{
    const response={mode:'production',status:'development_fixture_results',notice:'DEVELOPMENT_FIXTURE',is_recommendation:false} as PlanResult;
    expect(()=>assertMode(response,'production')).toThrow();
  });
  it('blocks a stale response from the previous mode',()=>{
    expect(()=>assertMode({mode:'development_fixture'} as PlanResult,'production')).toThrow();
  });
  it('requires fixtures to remain non-recommendations',()=>{
    expect(()=>assertMode({mode:'development_fixture',is_recommendation:true} as PlanResult,'development_fixture')).toThrow();
  });
});

describe('current-rotation comparison defaults',()=>{
  it('preselects the supported status-quo baseline and two alternatives',()=>{
    const result={existing_rotation_comparison:{status:'included',candidate_id:'b',crop_ids:['sunflower','aman_rice','sunflower'],reason:'supported'},candidate_rotations:[{id:'a'},{id:'b'},{id:'c'},{id:'d'}]} as unknown as PlanResult;
    expect(initialComparisonSelection(result)).toEqual(['b','a','c']);
  });
  it('does not invent a baseline when one was not supported',()=>{
    const result={existing_rotation_comparison:{status:'unsupported',candidate_id:null,crop_ids:['mung_bean','maize','aman_rice'],reason:'unsupported'},candidate_rotations:[{id:'a'},{id:'b'}]} as unknown as PlanResult;
    expect(initialComparisonSelection(result)).toEqual([]);
  });
});
