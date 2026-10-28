import {describe,expect,it} from 'vitest';
import {routeFromHash} from './routes';

describe('direct public routes',()=>{
  it('restores all public pages and Water Commons from refreshable hashes',()=>{for(const route of ['plan','water-commons','methodology','nasa','about','references'] as const)expect(routeFromHash(`#/${route}`)).toBe(route);expect(routeFromHash('')).toBe('landing');expect(routeFromHash('#/unknown')).toBe('landing')});
});
