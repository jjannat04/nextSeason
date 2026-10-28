export type Route='landing'|'plan'|'water-commons'|'methodology'|'nasa'|'about'|'references';
export function routeFromHash(hash:string):Route {const path=hash.replace(/^#\/?/,'').replace(/\/$/,'');return path==='plan'||path==='water-commons'||path==='methodology'||path==='nasa'||path==='about'||path==='references'?path:'landing'}
