/** Keep proxy/server HTML errors out of farmer-facing JSON error messages. */
export async function readApiBody(response:Response){
  if(!response.headers.get('content-type')?.includes('application/json'))throw new Error('The planning service did not return a valid response. Check the connection and retry.');
  try{return await response.json()}catch{throw new Error('The planning service returned invalid data. Please retry.')}
}
