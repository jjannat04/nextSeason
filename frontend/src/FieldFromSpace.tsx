import type {SpaceProfile,SourceProfile,Indicator} from './types';

const readable=(value:string)=>value.replaceAll('_',' ');
const format=(value:number|null|undefined,unit:string)=>value==null?'Unavailable':`${value.toLocaleString(undefined,{maximumFractionDigits:2})} ${unit}`;

export function indicatorText(indicator:Indicator|undefined) {
  if(!indicator || indicator.status!=='available')return 'Insufficient data for this comparison.';
  const labels:Record<string,string>={below_product_seasonal_median:'Root-zone moisture percentiles averaged below the NASA product’s seasonal median.',above_product_seasonal_median:'Root-zone moisture percentiles averaged above the NASA product’s seasonal median.',at_product_seasonal_median:'Root-zone moisture percentiles averaged at the NASA product’s seasonal median.',historical_rainfall_available:'Historical rainfall observations are available for the selected period.',drier_than_selected_comparison:'The selected period was drier than the matching historical comparison window.',wetter_than_selected_comparison:'The selected period was wetter than the matching historical comparison window.',equal_to_selected_comparison:'Rainfall matched the selected historical comparison window.'};
  return labels[indicator.value||'']||readable(indicator.value||'unknown');
}

function exactSource(source:SourceProfile) {
  return {product:source.product,period:source.period,spatial_resolution:source.spatial_resolution,temporal_resolution:source.temporal_resolution,
    variables:Object.fromEntries(Object.entries(source.series||{}).map(([key,value])=>[key,{unit:value.unit,mean:value.mean,total_mm:value.total_mm,total:value.total,coverage:value.coverage}])),
    observation_period:source.observation_period,coverage:source.coverage,cache_status:source.cache_status,access_status:source.access_status,reason:source.reason,
    provenance:source.provenance||{query:source.query,retrieved_at:source.retrieved_at,response_sha256:source.response_sha256,source_metadata:source.source_metadata}};
}

export default function FieldFromSpace({profile}:{profile:SpaceProfile}) {
  const cards=[
    {key:'power',name:'NASA POWER',tag:'Historical weather',symbol:'☀',source:profile.power,url:'https://power.larc.nasa.gov/docs/services/api/temporal/daily/',
      description:'Temperature history for the regional grid around your location.',impact:'Calendar-month temperature ranges influence each crop’s qualitative climate screening.',
      metric:format(profile.power.series?.T2M?.mean,'°C'),metricLabel:'Selected-period mean temperature',
      limitation:'Regional weather context, not an in-field measurement or a forecast.'},
    {key:'smap',name:'NASA SMAP',tag:'Surface & root-zone moisture',symbol:'◉',source:profile.smap,url:'https://nsidc.org/data/spl4smgp/versions/8',
      description:indicatorText(profile.interpreted_indicators.root_zone_moisture),impact:'Adds historical root-zone moisture context. The optional moisture preference compares observed exposure; it does not estimate crop damage or irrigation savings.',
      metric:format(profile.smap.series?.root_zone_soil_moisture?.mean,'m³/m³'),metricLabel:'Selected-period mean root-zone moisture',
      limitation:'9 km model-assimilated estimates; surface 0–5 cm and root zone 0–100 cm. No field-specific drought threshold is assumed.'},
    {key:'gpm',name:'NASA GPM IMERG',tag:'Historical precipitation',symbol:'☂',source:profile.gpm,url:'https://doi.org/10.5067/GPM/IMERGDF/DAY/07',
      description:indicatorText(profile.interpreted_indicators.historical_rainfall),impact:'A complete annual total can influence climate screening against published annual rainfall references. Short periods remain context only.',
      metric:format(profile.gpm.series?.precipitation?.total_mm,'mm'),metricLabel:'Selected-period precipitation total',
      limitation:'Final Run is delayed research data on a 0.1° grid. Rainfall is not irrigation demand, flood probability or a forecast.'}
  ];
  return <section id="evidence" className="panel space-profile"><div className="section-heading"><span className="step">05</span><div><span className="eyebrow">NASA EARTH OBSERVATIONS · HISTORICAL CONTEXT</span><h2>Your Field From Space</h2><p>Three independent sources, with their evidence and gaps kept visible.</p></div></div>
    <p className="hint">{profile.location.latitude}, {profile.location.longitude} · {profile.power.period?.start} — {profile.power.period?.end} · Regional grids around the selected point</p>
    <div className="space-sources">{cards.map(card=>{
      const available=card.source.status==='available';
      const partial=available && (Object.values(card.source.series||{}).some(s=>s.coverage && !s.coverage.complete) || Object.values(card.source.coverage||{}).some(s=>s && typeof s==='object' && 'complete' in s && s.complete===false));
      return <article className="space-source" key={card.key}><div className="space-source-heading"><span className="source-symbol" aria-hidden="true">{card.symbol}</span><div><h3>{card.name}</h3><span className="eyebrow">{card.tag}</span></div><span className="badge">{available?(partial?'Partial coverage':'Data available'):['pending','collecting'].includes(card.source.access_status||'')?'Processing':'Unavailable'}</span></div>
        <p>{available?card.description:'Observations from this source are unavailable for this request. No substitute values have been inserted.'}</p>
        <div className="space-metric"><span>{card.metricLabel}</span><strong>{card.metric}</strong></div>
        <div className="source-impact"><strong>Connection to your rotation options</strong><p>{available?card.impact:'This source has not affected your options. Supported evidence from the other sources can still be used.'}</p></div>
        <p className="hint">{card.limitation}</p><a href={card.url} target="_blank" rel="noreferrer">Source & product documentation ↗</a>
        <details><summary>Exact values, coverage & provenance</summary><pre>{JSON.stringify(exactSource(card.source),null,2)}</pre><details><summary>Time-indexed observations</summary><pre>{JSON.stringify(card.source.series,null,2)}</pre></details><ul>{card.source.limitations?.map((text,i)=><li key={i}>{text}</li>)}</ul></details>
      </article>;
    })}</div>
    <div className="space-interpretation"><span className="eyebrow">WHAT THE EVIDENCE SAYS</span><h3>Interpretation, before the satellite details.</h3><ul>{Object.entries(profile.interpreted_indicators).map(([key,indicator])=><li key={key}><strong>{readable(key)}</strong><p>{indicatorText(indicator)}</p>{indicator.status!=='available' && <p className="hint">{indicator.reason}</p>}<details><summary>Method, exact comparison & rotation impact</summary><p>{indicator.rotation_impact}</p><pre>{JSON.stringify(indicator,null,2)}</pre></details></li>)}</ul></div>
    <details><summary>Shared limitations and source status</summary><ul>{profile.limitations.map((text,i)=><li key={i}>{text}</li>)}</ul><pre>{JSON.stringify(profile.provider_status,null,2)}</pre></details>
  </section>;
}
