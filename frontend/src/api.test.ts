import {describe,expect,it} from 'vitest';
import {readApiBody} from './api';

describe('API failure copy',()=>{
  it('rejects proxy HTML and malformed JSON without exposing server markup',async()=>{await expect(readApiBody(new Response('<html>server error</html>',{status:503,headers:{'content-type':'text/html'}}))).rejects.toThrow('planning service did not return a valid response');await expect(readApiBody(new Response('{broken',{status:502,headers:{'content-type':'application/json'}}))).rejects.toThrow('planning service returned invalid data')});
});
