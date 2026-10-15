"""Single-pass tolerant decoding; formatting defects never cause model retries."""
import json,re

def decode(raw):
 if not isinstance(raw,str) or not raw.strip() or len(raw)>20000:raise ValueError('empty or oversized reply')
 text=raw.strip();text=re.sub(r'^```(?:json)?\s*|\s*```$', '',text,flags=re.I).strip()
 value=None
 try:value=json.loads(text)
 except (ValueError,TypeError):
  start=text.find('{')
  if start>=0:
   try:value=json.JSONDecoder().raw_decode(text[start:])[0]
   except ValueError:pass
 if isinstance(value,dict):
  if not any(isinstance(value.get(k),str) and value[k].strip() for k in ['response','message','content','question','follow_up_question']) and not text.startswith('{'):
   prefix=text[:text.find('{')].strip()
   if re.search(r'[A-Za-z\u3400-\u9fff]',prefix):value['response']=prefix
  return value
 if value is not None:raise ValueError('unusable response structure')
 # A truncated JSON envelope may still contain a complete visible reply string.
 if text.startswith('{'):
  for field in ['response','question','message','content']:
   match=re.search(r'"'+field+r'"\s*:\s*',text)
   if match:
    try:
     visible=json.JSONDecoder().raw_decode(text[match.end():])[0]
     if isinstance(visible,str) and visible.strip():return {'response':visible}
    except ValueError:pass
  raise ValueError('unusable JSON envelope')
 if text.startswith(('[','```')) or not re.search(r'[A-Za-z\u3400-\u9fff]',text):raise ValueError('unusable visible reply')
 return {'response':text}

def visible_reply(value,user_texts,language='English'):
 response=next((value.get(k) for k in ['response','message','content','question','follow_up_question'] if isinstance(value.get(k),str) and value[k].strip()),'')
 if not response:raise ValueError('no visible reply')
 question=value.get('question',value.get('follow_up_question',''))
 if isinstance(question,str) and question.strip() and not any(c in response for c in '?？') and question.strip() not in response and len(response)+len(question)<1600:
  response=response.rstrip()+' '+question.strip()
 response=response.strip()
 # Preserve ordinary comparative signs and quoted user views. React displays plain text.
 # Repair only narrow, unambiguous assistant sign-off instructions or unsupported absence.
 sentences=re.split(r'(?<=[。！？!?])\s*|(?<=\.)\s+',response)
 kept=[];repaired=False
 for sentence in sentences:
  if not sentence:continue
  directive=re.search(r'^\s*(?:you\s+(?:must|should)\s+(?:sign|approve|decline)\b|你(?:应当|必须|可以)(?:签字|批准|拒绝)|(?:已(?:经)?违反|构成违规))',sentence,re.I)
  if directive and not sentence.rstrip().endswith(('?','？')):repaired=True;continue
  assumed=re.search(r'(?:既然|因为|已知|since|given that).{0,120}?(无人检查|无人复核|没人检查|没人复核|nobody reviewed|no one reviewed|nobody checked|no one checked)',sentence,re.I)
  if assumed and not any(assumed.group(1).casefold() in text.casefold() for text in user_texts):
   kept.append('是否有人复核仍待确认。' if language=='中文' else 'Whether anyone reviewed this remains unconfirmed.');repaired=True;continue
  kept.append(sentence)
 result=('' if language=='中文' else ' ').join(kept).strip()
 if not result or repaired and not any(c in result for c in '?？'):
  result+=(' 建议先核实依据，再由人作出判断。你可以从哪项资料开始核实？' if language=='中文' else ' Verify the supporting information before a human decision. Which source could you check first?')
 # Soft length normalisation, not rejection. Prefer complete sentences.
 if len(result)>1600:
  result=result[:1500];ends=list(re.finditer(r'[。.!?？]',result))
  if ends:result=result[:ends[-1].end()]
 return result.strip()
