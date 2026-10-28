import {describe,it,expect} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import FieldFromSpace,{indicatorText} from './FieldFromSpace';
import type {SpaceProfile} from './types';

const profile={location:{latitude:22.8,longitude:89.55},power:{status:'available',period:{start:'2024-01-01',end:'2024-12-31'},series:{T2M:{mean:22}},cache_status:'cached'},smap:{status:'unavailable',access_status:'authentication_required',series:{}},gpm:{status:'unavailable',access_status:'authentication_required',series:{}},interpreted_indicators:{root_zone_moisture:{status:'insufficient_data',value:null,reason:'SMAP unavailable'},historical_rainfall:{status:'insufficient_data',value:null,reason:'IMERG unavailable'}},provider_status:{power:{status:'available'},smap:{status:'unavailable'},gpm:{status:'unavailable'}},provenance:{},limitations:['Historical regional observations, not field measurements.']} as SpaceProfile;

describe('Your Field From Space',()=>{
  it('keeps every provider visible when two are unavailable',()=>{
    const html=renderToStaticMarkup(<FieldFromSpace profile={profile}/>);
    expect(html).toContain('Your Field From Space');
    for(const name of ['NASA POWER','NASA SMAP','NASA GPM IMERG'])expect(html).toContain(name);
    expect(html).toContain('22 °C');expect(html).toContain('Unavailable');
  });
  it('never invents zero precipitation or soil moisture for failed providers',()=>{
    const html=renderToStaticMarkup(<FieldFromSpace profile={profile}/>);
    expect(html).not.toContain('0 mm');expect(html).not.toContain('0 m³/m³');
    expect(html).toContain('This source has not affected your options.');
  });
  it('keeps exact data and provenance in closed disclosures',()=>{
    const html=renderToStaticMarkup(<FieldFromSpace profile={profile}/>);
    expect(html).toContain('<details><summary>Exact values, coverage &amp; provenance</summary>');
    expect(html).not.toContain('<details open');
    expect(html).toContain('Source &amp; product documentation');
  });
  it('distinguishes a supported seasonal median from missing evidence',()=>{
    expect(indicatorText({status:'available',value:'below_product_seasonal_median'})).toContain('below');
    expect(indicatorText({status:'insufficient_data',value:null})).toContain('Insufficient data');
  });
});
