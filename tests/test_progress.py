import json,unittest
from inquiry.core import Session,parse_turn,ModelOutputError
from inquiry.analysis import empty_analysis,apply_updates,finish,validate_brief

def u(area,facet,quote,turn=1,kind='reported'):
 return dict(area=area,facet=facet,quote=quote,turn=turn,kind=kind,basis='A source-supported statement.',replaces=[])
class ReplyToleranceTests(unittest.TestCase):
 def test_normal_prose_missing_question_mark_multiple_questions_and_fences_are_usable(self):
  for raw in ['先保留未知，再核实原始资料。','I understand. What could you check? Who could help?',json.dumps({'response':'You could first verify the records.','focus':'evidence'}),'```json\n'+json.dumps({'question':'能核实吗','focus':'review'})+'\n```']:
   with self.subTest(raw=raw):self.assertTrue(parse_turn(raw,['不知道'],empty_analysis(),'中文')[0])
 def test_missing_optional_metadata_does_not_discard_the_reply(self):
  text,focus,quotes,a=parse_turn(json.dumps({'response':'Keep the uncertainty explicit. What could you check?','focus':'unknown','observations':{},'analysis':None}),['I am not sure'],empty_analysis(),'English')
  self.assertIn('uncertainty',text);self.assertEqual(focus,'scope')
 def test_an_unreported_absence_is_repaired_without_losing_the_turn(self):
  text,*_=parse_turn(json.dumps({'question':'Since nobody reviewed the entries, who should review them?','focus':'review'}),['I do not know whether anyone reviewed the entries.'],empty_analysis(),'English')
  self.assertNotIn('Since nobody reviewed',text)
 def test_short_uncertainty_refusal_and_controversial_stance_are_not_invalid_inputs(self):
  class Client:
   def complete(self,m):return json.dumps({'response':'That is your stated position. What would follow from it?','focus':'interests'}),{}
  for text in ['不知道','我不确定','我不想回答','我不打算解决这个问题','我觉得个人利益更重要','我愿意承担风险']:
   s=Session();s.submit(text,Client(),'中文');self.assertEqual(s.turns,1)
 def test_empty_and_unusable_structure_still_fail(self):
  for raw in ['', '{}', '{"api_key":"not-a-response"}', '```json\n{"analysis":']:
   with self.subTest(raw=raw),self.assertRaises(ModelOutputError):parse_turn(raw,['Unknown'],empty_analysis(),'English')
class DualProgressTests(unittest.TestCase):
 def test_unknown_increases_exploration_without_information_and_deduplicates(self):
  from inquiry.progress import record_engagements
  a=empty_analysis();a['question_target']={'area':'review','facet':'reviewer'}
  a=record_engagements(a,[],['Initial situation','不知道'],{'area':'review','facet':'reviewer'})
  d=finish(a)['dimensions']['review'];self.assertEqual(d['coverage'],1);self.assertEqual(d['information'],0)
  a=record_engagements(a,[],['Initial situation','不知道','不知道'],{'area':'review','facet':'reviewer'})
  self.assertEqual(finish(a)['dimensions']['review']['coverage'],1)
 def test_decline_is_recorded_and_a_subsequent_question_can_move_on(self):
  from inquiry.progress import record_engagements
  a=record_engagements(empty_analysis(),[],['Situation','我不想回答'],{'area':'interests','facet':'influence'})
  d=finish(a)['dimensions']['interests'];self.assertEqual(d['coverage'],1);self.assertIn('influence',d['declined']);self.assertEqual(d['information'],0)
 def test_initial_facts_preserved_and_position_is_not_graded_for_morality(self):
  a=apply_updates(empty_analysis(),[u('interests','influence','我觉得个人利益更重要')],['我觉得个人利益更重要'])
  self.assertEqual(a['dimensions']['interests']['coverage'],1);self.assertEqual(a['dimensions']['interests']['information'],1)
 def test_conditional_advice_does_not_need_all_five_dimensions(self):
  from inquiry.progress import update_context
  text='I must decide whether to report an error. A bonus depends on silence. I want independent review. Investors may be harmed.'
  a=apply_updates(empty_analysis(),[u('role','decision','I must decide whether to report an error.'),u('pressure','incentive','A bonus depends on silence.'),u('review','route','I want independent review.'),u('role','responsibility','Investors may be harmed.')],[text])
  a=update_context(a,{'conflict':{'summary':'Silence for a bonus conflicts with reporting the error.','basis_quotes':['I must decide whether to report an error.','A bonus depends on silence.']},'stance':{'summary':'Wants independent review.','basis_quotes':['I want independent review.']},'stakeholders':{'summary':'Investors.','basis_quotes':['Investors may be harmed.']},'consequences':{'summary':'Potential harm to investors.','basis_quotes':['Investors may be harmed.']},'critical_unknowns':[]},[text])
  r=finish(a)['readiness'];self.assertTrue(r['eligible']);self.assertLess(sum(v['coverage'] for v in a['dimensions'].values()),15)
  b={'conflict':'A reported conflict.','stakeholders':'Investors.','options':[{'action':'Seek review','tradeoff':'Requires an independent route.'}],'recommendation':'If feasible, consider independent review.','uncertainties':['The route needs checking.'],'basis_quotes':['I want independent review.']}
  self.assertIsNotNone(validate_brief(b,a,[text],'English'))
 def test_new_uncertainty_can_lower_information_and_readiness_without_erasing_exploration(self):
  from inquiry.progress import record_engagements
  a=apply_updates(empty_analysis(),[u('evidence','basis','The full ledger is available.')],['The full ledger is available.'])
  b=record_engagements(a,[],['The full ledger is available.','I cannot confirm'],{'area':'evidence','facet':'basis'});b=finish(b)
  self.assertEqual(b['dimensions']['evidence']['coverage'],1);self.assertEqual(b['dimensions']['evidence']['information'],0);self.assertLessEqual(b['readiness']['score'],a['readiness']['score'])
class ExtendedConversationTests(unittest.IsolatedAsyncioTestCase):
 async def test_gemini_and_glm_each_accept_twenty_turns_without_deleting_or_double_calling(self):
  from edge.service import Service,APIError
  from edge.store import MemoryStore
  class Transport:
   def __init__(self):self.calls=[]
   async def complete(self,p,m,k,messages):
    self.calls.append(messages)
    return json.dumps({'response':'You can leave this unknown and consider another angle.','focus':'review','question_target':{'area':'review','facet':'route'}}),{}
  for provider,model in [('gemini','gemini-2.5-flash'),('zhipu','glm-4.7-flash')]:
   t=Transport();service=Service(MemoryStore(),t,{'GEMINI_API_KEY':'fixture','ZHIPU_API_KEY':'fixture','GEMINI_FREE_TIER_CONFIRMED':'true','ZHIPU_FREE_TIER_CONFIRMED':'true','DEMO_ACCESS_ENABLED':'true'});token,s=await service.create()
   for i in range(20):
    body={'provider':provider,'model':model,'language':'English','consent':True,'version':s['version'],'request_id':f'extended-turn-{i:02}','text':'Fictional information: '+('x'*3800 if i%2==0 else 'I do not know.')}
    s=([e async for e in service.inquire(token,body)])[-1]['data']
   self.assertEqual(len(s['session']['messages']),40);self.assertEqual(len(s['session']['records']),20);self.assertEqual(len(t.calls),20)
   self.assertLessEqual(max(sum(len(m['content']) for m in call[1:]) for call in t.calls),26000)
   self.assertEqual(s['session']['messages'][0]['content'], 'Fictional information: '+'x'*3800)
   with self.assertRaises(APIError):[e async for e in service.inquire(token,{**body,'version':s['version'],'request_id':'extended-turn-21'})]
   self.assertEqual(len((await service.restore(token))['session']['messages']),40)
class FocusedEngagementTests(unittest.TestCase):
 def test_short_unknown_cannot_fill_unrelated_dimensions_from_noisy_model_metadata(self):
  previous=empty_analysis();previous['question_target']={'area':'review','facet':'reviewer'}
  raw=json.dumps({'response':'Unknown is acceptable. Let us consider your role.','focus':'role','analysis':{'updates':[u('pressure','incentive','不知道',2)],'engagements':[dict(area='pressure',facet='incentive',quote='不知道',turn=2,state='unknown')]}})
  a=parse_turn(raw,['Fictional audit concern.','不知道'],previous,'中文')[3]
  self.assertEqual(a['dimensions']['review']['coverage'],1);self.assertEqual(a['dimensions']['pressure']['coverage'],0)
 def test_repeated_unknown_after_new_known_information_reopens_sufficiency(self):
  from inquiry.progress import record_engagements
  texts=['Situation','不知道','The full ledger is now available.','不知道'];target={'area':'evidence','facet':'basis'}
  a=record_engagements(empty_analysis(),[],texts[:2],target);a=apply_updates(a,[u('evidence','basis',texts[2],3)],texts[:3]);self.assertEqual(a['dimensions']['evidence']['information'],1)
  a=finish(record_engagements(a,[],texts,target));self.assertEqual(a['dimensions']['evidence']['information'],0)
class ReviewRegressionTests(unittest.TestCase):
 def test_blank_quotes_cannot_manufacture_readiness_signals(self):
  from inquiry.progress import update_context
  a=apply_updates(empty_analysis(),[u('role','position','I handle the records.')],['I handle the records.'])
  b=update_context(a,{'conflict':{'summary':'Invented conflict','basis_quotes':['','   ']}},['I handle the records.'])
  self.assertNotIn('conflict',b['context']['signals'])
 def test_usable_prose_before_optional_json_is_retained(self):
  reply=parse_turn('We can leave that uncertain. Which records can you check?\n{"analysis":{"updates":[]}}',['I do not know'],empty_analysis(),'English')[0]
  self.assertIn('Which records',reply)
 def test_regenerate_cannot_attribute_previous_unknown_to_new_question(self):
  a=empty_analysis();a['question_target']={'area':'evidence','facet':'basis'}
  raw=json.dumps({'response':'Who could independently review this?','focus':'review','question_target':{'area':'review','facet':'reviewer'}})
  a=parse_turn(raw,['Situation','I do not know'],a,'English')[3]
  self.assertEqual(a['dimensions']['evidence']['coverage'],1)
  b=parse_turn(raw,['Situation','I do not know'],a,'English',regenerating=True)[3]
  self.assertEqual(b['dimensions']['review']['coverage'],0)
 def test_broad_source_quote_does_not_let_unrelated_uncertainty_hide_grounded_signals(self):
  from inquiry.progress import update_context
  text='I must report the error. Investors could lose money. I do not know the source.'
  a=apply_updates(empty_analysis(),[u('role','decision','I must report the error.'),u('role','responsibility','Investors could lose money.'),u('evidence','basis','I do not know the source.',kind='uncertain')],[text])
  a=update_context(a,{'conflict':dict(summary='Reporting an error affects investors.',basis_quotes=[text])},[text])
  self.assertTrue(finish(a)['readiness']['criteria']['conflict'])
 def test_frontend_guidance_request_is_an_explicit_early_advice_request(self):
  from inquiry.analysis import wants_advice
  self.assertTrue(wants_advice('Please give brief conditional guidance from what we know.'))
 def test_unique_exact_quote_recovers_a_model_mislabelled_turn_without_guessing(self):
  from inquiry.progress import source_turns
  users=['The initial concern.','I can check the contracts.']
  raw=u('evidence','basis',users[1],1)
  a=parse_turn(json.dumps({'response':'What would you verify first?','analysis':{'updates':[raw]}}),users,empty_analysis(),'English')[3]
  self.assertEqual(a['facts'][0]['turn'],2)
  self.assertEqual(source_turns([u('evidence','basis','repeat',99)],['repeat','repeat'])[0]['turn'],99)
 def test_reply_question_already_present_is_not_appended_again(self):
  r=parse_turn(json.dumps({'response':'What records can you check?','question':'What records can you check ?'}),['Unknown'],empty_analysis(),'English')[0]
  self.assertEqual(r.count('?'),1)
 def test_unknown_or_declined_exact_target_is_not_immediately_repeated(self):
  a=empty_analysis();a['question_target']={'area':'review','facet':'reviewer'}
  raw=json.dumps({'response':'Who could review it?','focus':'review','question_target':a['question_target']})
  for answer in ['I do not know','I do not want to answer']:
   reply,focus,_,next_state=parse_turn(raw,['Concern',answer],a,'English')
   self.assertNotEqual(next_state['question_target'],a['question_target']);self.assertNotEqual(focus,'review')
   self.assertEqual(next_state['dimensions']['review']['coverage'],1)
 def test_misnumbered_generic_refusal_cannot_become_reported_facts(self):
  a=empty_analysis();a['question_target']={'area':'review','facet':'reviewer'}
  raw=json.dumps({'response':'We can consider another angle.','analysis':{'updates':[u('pressure','incentive','I do not want to answer',1)]}})
  b=parse_turn(raw,['Initial situation','I do not want to answer'],a,'English')[3]
  self.assertEqual(b['dimensions']['pressure']['information'],0)
  self.assertEqual(b['dimensions']['review']['coverage'],1)
 def test_chinese_export_preserves_unknown_source_and_localised_measures(self):
  from inquiry.progress import record_engagements
  from inquiry.analysis import analysis_markdown
  a=finish(record_engagements(empty_analysis(),[],['Situation','不知道'],{'area':'review','facet':'reviewer'}))
  text=analysis_markdown(a,'中文')
  for value in ['探索覆盖度','信息充分度','建议准备度','已探索 · 仍未知','不知道']:self.assertIn(value,text)
  self.assertNotIn('exploring',text)
