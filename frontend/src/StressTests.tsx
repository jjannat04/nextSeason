import {useState} from 'react';
import type {Candidate,StressScenario,StressTests as StressData} from './types';
import './stress.css';

const scenarios=[
  ['historical_normal','Normal','Near the observed sample median'],
  ['historical_dry','Dry','Lowest observed annual precipitation'],
  ['historical_hot','Hot','Highest observed annual mean temperature'],
  ['historical_wet','Wet','Highest observed annual precipitation'],
] as const;
type ScenarioKey=typeof scenarios[number][0];
const readable=(value:string)=>value.replaceAll('_',' ');
const category=(value:string|null|undefined)=>value?readable(value):'Insufficient data';
const amount=(value:number|undefined,unit:string)=>value==null?'Unknown':`${value.toLocaleString(undefined,{maximumFractionDigits:1})} ${unit}`;

export default function StressTests({data,candidates}:{data:StressData;candidates:Candidate[]}) {
  const [selected,setSelected]=useState<ScenarioKey>('historical_normal');
  const active=data[selected] as StressScenario;
  const supported=data.baseline.status==='supported';
  return <section id="stress-tests" className="panel stress-tests" aria-labelledby="stress-title">
    <div className="section-heading"><span className="step">09</span><div><span className="eyebrow">HISTORICAL ENVIRONMENTAL STRESS TEST</span><h2 id="stress-title">How Does This Rotation Hold Up?</h2><p>Compare the existing crop sequences under contrasting observed years at your location.</p></div></div>
    <div className="stress-notice"><strong>Based on historical environmental scenarios, not a forecast.</strong><p>These are observed NASA environmental conditions from the 2015–2024 sample. Labels describe that sample; they are not probabilities, predicted weather, crop losses or irrigation estimates.</p></div>
    {!supported && <p className="stress-unavailable" role="status">Stress tests need ten complete annual NASA POWER records. Missing baseline years: {data.baseline.missing_years?.join(', ')||'unknown'}. No scenario was invented.</p>}
    <div className="stress-tabs" role="tablist" aria-label="Historical climate scenarios">{scenarios.map(([key,label,description])=>{
      const item=data[key];return <button key={key} id={`stress-tab-${key}`} type="button" role="tab" aria-selected={selected===key} aria-controls="stress-panel" className={`stress-tab ${selected===key?'selected':''}`} onClick={()=>setSelected(key)}><span>{label}</span><strong>{item.selected_year??'Unavailable'}</strong><small>{description}</small></button>;
    })}</div>
    <div id="stress-panel" role="tabpanel" aria-labelledby={`stress-tab-${selected}`} className="stress-scenario-panel">
      {active.environmental_conditions ? <><div className="stress-scenario-summary"><div><span className="eyebrow">OBSERVED {active.selected_year}</span><h3>{scenarios.find(([key])=>key===selected)?.[1]} year in this sample</h3><p>{scenarios.find(([key])=>key===selected)?.[2]}</p></div><div className="stress-metrics"><div><span>Annual mean temperature</span><strong>{amount(active.environmental_conditions.annual_mean_t2m_c,'°C')}</strong><small>Sample median: {amount(active.environmental_conditions.baseline_medians.annual_mean_t2m_c,'°C')}</small></div><div><span>Annual precipitation</span><strong>{amount(active.environmental_conditions.annual_precipitation_mm,'mm')}</strong><small>Sample median: {amount(active.environmental_conditions.baseline_medians.annual_precipitation_mm,'mm')}</small></div></div></div><details><summary>Why this scenario? NASA source and method</summary><p>{active.environmental_conditions.classification_rule}</p><p>Ranks among {active.environmental_conditions.sample_size} complete observed years: temperature {active.environmental_conditions.temperature_rank_low_to_high} of {active.environmental_conditions.sample_size}; precipitation {active.environmental_conditions.precipitation_rank_low_to_high} of {active.environmental_conditions.sample_size} (low to high).</p><pre>{JSON.stringify(active.provenance,null,2)}</pre></details></>:<p role="status">{active.limitations.join(' ')}</p>}
    </div>
    {supported && <><div className="stress-compare-heading"><h3>Rotation comparison</h3><p>Qualitative reference screens only. A concern means the observed year fell outside a published species range; it does not predict crop failure.</p></div><div className="stress-rotation-grid">{candidates.map((candidate,index)=>{
      const robustness=data.robustness.by_candidate[candidate.id];
      const best=data.robustness.most_robust_candidate_ids.includes(candidate.id);
      const current=active.rotation_interpretation[candidate.id];
      return <article className={`stress-rotation-card ${best?'stress-best':''}`} key={candidate.id}><div className="stress-card-head"><div><span className="eyebrow">OPTION {index+1}</span><h4>{candidate.activities.map(item=>item.label).join(' → ')}</h4></div>{best && <span className="stress-best-badge">Most Robust{data.robustness.most_robust_candidate_ids.length>1?' (tie)':''}</span>}</div><p><strong>{robustness?.label?category(robustness.label):'Insufficient data'}</strong>{robustness?.label==='sensitive' && best ? ' · fewest concerning years in this sample; still sensitive overall' : ''}</p><div className="stress-trajectory" aria-label={`Scenario interpretations for ${candidate.activities.map(item=>item.label).join(', ')}`}>{scenarios.map(([key,label])=>{
        const item=data[key].rotation_interpretation[candidate.id];return <div key={key} className={selected===key?'active':''}><span>{label} · {data[key].selected_year}</span><strong className={`stress-category ${item?.value||'unknown'}`}>{category(item?.value)}</strong></div>;
      })}</div>{current && <details><summary>Selected scenario crop comparisons</summary><p>Temperature: {current.temperature?.map((part,index)=>`${candidate.activities[index]?.label}: ${category(part.value)}`).join(' · ')||'Insufficient data'}</p><p>Annual rainfall reference: {current.annual_rainfall?.map((part,index)=>`${candidate.activities[index]?.label}: ${category(part.value)}`).join(' · ')||'Insufficient data'}</p><p>{current.method||current.reason}</p><p>Water demand, salinity, stage damage, yield and income remain insufficient data.</p></details>}</article>;
    })}</div><p className="hint">{data.robustness.selection_rule}</p></>}
    <details><summary>Limits and exact baseline period</summary><p>Baseline: {data.baseline.period?.start||'Unavailable'} to {data.baseline.period?.end||'Unavailable'}. Complete observed years: {data.baseline.sample_size??'Unknown'}.</p><ul>{active.limitations.map(limit=><li key={limit}>{limit}</li>)}</ul></details>
  </section>;
}
