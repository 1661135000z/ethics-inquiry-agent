"""Deterministic bounded request context; accepted transcript is never compressed/deleted."""
FREE_TURN_LIMIT=20
ATTEMPT_LIMIT=48
TRANSCRIPT_LIMIT=120000

def model_history(candidate,budget=24000):
 if len(candidate)<=2:return candidate
 # Preserve the first exchange and the newest user input; retain recent complete pairs.
 # Older factual context remains in the source-linked analysis in the system prompt.
 first=candidate[:2];tail=candidate[2:];chunks=[tail[i:i+2] for i in range(0,len(tail),2)]
 used=sum(len(m['content']) for m in first);kept=[]
 for chunk in reversed(chunks):
  size=sum(len(m['content']) for m in chunk)
  if not kept or used+size<=budget:kept.insert(0,chunk);used+=size
  else:break
 selected=first+[m for pair in kept for m in pair]
 if len(selected)==len(candidate):return candidate
 turns={id(m):i//2+1 for i,m in enumerate(candidate)}
 return [{'role':m['role'],'content':f"[{'User turn' if m['role']=='user' else 'Assistant after turn'} {turns[id(m)]}; original text follows]\n{m['content']}"} for m in selected]
