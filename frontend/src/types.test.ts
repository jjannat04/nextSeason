import {describe,it,expect} from 'vitest';
import {assertMode} from './types';
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
