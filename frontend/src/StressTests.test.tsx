import {describe,it,expect} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import StressTests from './StressTests';
import type {Candidate,StressTests as StressData,StressScenario} from './types';

const conditions={annual_mean_t2m_c:25.9,annual_precipitation_mm:2400,temperature_rank_low_to_high:5,precipitation_rank_low_to_high:5,sample_size:10,classification_rule:'Recorded sample medoid rule',baseline_medians:{annual_mean_t2m_c:25.8,annual_precipitation_mm:2300}};
const scenario=(year:number):StressScenario=>({evidence_status:'supported',selected_year:year,environmental_conditions:conditions,rotation_interpretation:{one:{status:'qualitative_screening',value:'acceptable',temperature:[{status:'qualitative_screening',value:'acceptable'}],annual_rainfall:[{status:'qualitative_screening',value:'good_fit'}],unsupported_dimensions:{irrigation_demand:{status:'insufficient_data'}}}},provenance:{provider:'NASA POWER',product:'daily point AG',response_sha256:'recorded-checksum'},limitations:['Historical observation, not a forecast.']});
const data:StressData={historical_normal:scenario(2024),historical_dry:scenario(2022),historical_hot:scenario(2016),historical_wet:scenario(2017),baseline:{status:'supported',period:{start:'2015-01-01',end:'2024-12-31'},sample_size:10},robustness:{by_candidate:{one:{status:'supported',label:'moderately_robust',concerning_distinct_years:[2017]}},most_robust_candidate_ids:['one'],selection_rule:'Fewest concerning distinct years.'},notice:'Historical observations, not a forecast.'};
const candidates=[{id:'one',rank:1,activities:[{crop_id:'maize',label:'Maize',planting:'Nov',harvest:'Mar'}]}] as Candidate[];

describe('historical stress screen',()=>{
  it('shows four observed scenarios and the historical-not-forecast notice',()=>{
    const html=renderToStaticMarkup(<StressTests data={data} candidates={candidates}/>);
    for(const name of ['Normal','Dry','Hot','Wet'])expect(html).toContain(name);
    expect(html).toContain('Based on historical environmental scenarios, not a forecast.');
    expect(html).toContain('Most Robust');
    expect(html).toContain('NASA POWER');
    expect(html).not.toContain('/100');
    expect(html).not.toContain('yield loss');
  });
  it('reports missing baseline without manufacturing scenario conditions',()=>{
    const missing={...data,baseline:{status:'insufficient_data',missing_years:[2022]},historical_normal:{...data.historical_normal,selected_year:null,environmental_conditions:null,evidence_status:'insufficient_data'}} as StressData;
    const html=renderToStaticMarkup(<StressTests data={missing} candidates={candidates}/>);
    expect(html).toContain('Missing baseline years: 2022');
    expect(html).toContain('No scenario was invented');
  });
});
