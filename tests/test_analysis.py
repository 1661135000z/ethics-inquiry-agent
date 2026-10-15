import json
import unittest
from inquiry.analysis import empty_analysis, apply_updates, dimension_states, seed_case, analysis_context
from inquiry.core import Session, ModelOutputError

def update(area,facet,quote,turn=1,kind='reported',replaces=None):
    return dict(area=area,facet=facet,quote=quote,turn=turn,kind=kind,basis='The user explicitly states this.',replaces=replaces or [])

class AnalysisTests(unittest.TestCase):
    def test_case_seed_has_traceable_relationship_not_invented_pressure(self):
        from inquiry.examples import EXAMPLES
        case=next(c for c in EXAMPLES if c['id']=='relationships')
        a=seed_case(case,'English')
        ties=[f for f in a['facts'] if f['area']=='interests']
        self.assertTrue(any('close friend from university' in f['quote'] for f in ties))
        self.assertEqual(dimension_states(a)['interests']['status'],'partial')
        for f in a['facts']: self.assertIn(f['quote'],case['text_en'])
        blank=seed_case(next(c for c in EXAMPLES if c['id']=='dashboard'),'English')
        self.assertFalse(any(f['area']=='interests' for f in blank['facts']))

    def test_exact_source_unknown_and_multidimensional_support(self):
        texts=['The CFO is my old classmate. My boss tied promotion to silence. I do not know who reviewed the file.']
        a=apply_updates(empty_analysis(),[update('interests','relationship','The CFO is my old classmate.'),update('pressure','incentive','My boss tied promotion to silence.'),update('review','reviewer','I do not know who reviewed the file.',kind='uncertain'),update('role','responsibility','Nobody reviewed anything.')],texts)
        self.assertEqual({f['area'] for f in a['facts']},{'interests','pressure','review'})
        self.assertIn('reviewer',dimension_states(a)['review']['missing'])
        self.assertEqual(dimension_states(a)['review']['coverage'],0)
        self.assertEqual(dimension_states(a)['pressure']['coverage'],1)

    def test_repeat_and_nested_quote_do_not_accumulate_coverage(self):
        text='The CFO and I have been close friends since university.'
        a=apply_updates(empty_analysis(),[update('interests','relationship',text)], [text])
        b=apply_updates(a,[update('interests','relationship','close friends since university',2)], [text,'close friends since university'])
        self.assertEqual(len(b['facts']),1)
        self.assertEqual(dimension_states(a),dimension_states(b))
        c=apply_updates(b,[update('interests','relationship','We went to university together.',3)], [text,'close friends since university','We went to university together.'])
        self.assertEqual(dimension_states(c)['interests']['coverage'],1)

    def test_new_fact_can_retract_prior_support_and_reopen_dimension(self):
        texts=['An independent partner reviewed the file.','Correction: I cannot confirm any review occurred.']
        a=apply_updates(empty_analysis(),[update('review','reviewer',texts[0])],texts[:1])
        b=apply_updates(a,[update('review','reviewer',texts[1],2,'uncertain',[a['facts'][0]['id']])],texts)
        self.assertEqual(dimension_states(b)['review']['coverage'],0)
        self.assertEqual(b['facts'][0]['status'],'superseded')
        self.assertEqual(b['facts'][1]['kind'],'uncertain')
        bad=apply_updates(a,[update('pressure','request',texts[1],2,'uncertain',[a['facts'][0]['id']])],texts)
        self.assertEqual(bad['facts'][0]['status'],'active')

    def test_state_context_includes_boundaries_unknowns_and_not_a_risk_score(self):
        context=analysis_context(empty_analysis(),'English')
        self.assertIn('relationship',context)
        self.assertIn('promotion',context)
        self.assertIn('missing',context)
        self.assertIn('not a risk score',context)

    def test_same_model_call_updates_analysis_and_conditional_advice(self):
        class Client:
            def __init__(self): self.calls=[]
            def complete(self,messages):
                self.calls.append(messages)
                return json.dumps({'question':'Who could independently check the report?','response':'A private friendship may affect your judgment. Who could independently check the report?','focus':'review','observations':[], 'analysis':{'updates':[update('interests','relationship','The CFO is my university classmate.')]}}),{'provider':'gemini','model':'test'}
        c=Client();s=Session();s.submit('The CFO is my university classmate.',c)
        self.assertEqual(len(c.calls),1)
        self.assertIn('university classmate',s.analysis['facts'][0]['quote'])
        self.assertTrue(s.messages[-1]['content'].startswith('A private friendship'))
        s.submit('I do not know who checked it.',c,'中文')
        prompt=c.calls[-1][0]['content']
        self.assertIn('中文',prompt)
        self.assertIn('relationship',prompt)
        self.assertIn('information gaps',prompt)

    def test_invalid_response_is_atomic(self):
        class Client:
            def complete(self,messages): return json.dumps({'question':'Who could review this?','focus':'review','response':'You should sign the audit. Who could review this?','analysis':{'updates':[]}}),{}
        s=Session()
        with self.assertRaises(ModelOutputError):s.submit('The CFO is my university classmate.',Client())
        self.assertEqual(s.messages,[])
        self.assertEqual(s.analysis['facts'],[])

if __name__=='__main__':unittest.main()

class AdviceStateTests(unittest.TestCase):
    def full_state(self):
        from inquiry.analysis import DEFINITIONS
        texts=[];updates=[]
        for area,d in DEFINITIONS.items():
            for facet in d['facets']:
                quote=f'User explicitly describes {area} {facet} for this audit decision.'
                texts.append(quote)
                updates.append(update(area,facet,quote,len(texts)))
        return apply_updates(empty_analysis(),updates,texts),texts

    def test_ready_requires_distinct_supported_facets_not_turns(self):
        a,texts=self.full_state()
        self.assertTrue(a['ready'])
        b=apply_updates(empty_analysis(),[update('pressure','request',t,i+1) for i,t in enumerate(texts)],texts)
        self.assertFalse(b['ready'])
        self.assertEqual(dimension_states(b)['pressure']['coverage'],1)

    def test_brief_is_conditional_source_linked_and_reopened_by_new_facts(self):
        from inquiry.analysis import validate_brief
        a,texts=self.full_state()
        brief={'conflict':'Reported interest versus independent judgment.','stakeholders':'The reported audit team.',
          'options':[{'action':'Check original records','tradeoff':'May delay closure'},{'action':'Seek independent review','tradeoff':'Depends on availability'}],
          'recommendation':'If the records support the concern, consider independent review before deciding.',
          'uncertainties':['The records still need independent verification.'],'basis_quotes':[texts[0]]}
        a['brief']=validate_brief(brief,a,texts,'English')
        self.assertIsNotNone(a['brief'])
        new='Correction: I cannot confirm the responsibilities attributed to me.'
        old=next(f for f in a['facts'] if f['area']=='role' and f['facet']=='responsibility')
        b=apply_updates(a,[update('role','responsibility',new,len(texts)+1,'uncertain',[old['id']])],texts+[new])
        self.assertFalse(b['ready']);self.assertTrue(b['brief']['stale'])
        self.assertIsNone(validate_brief(brief,b,texts+[new],'English'))
        early=apply_updates(empty_analysis(),[update('role','position',texts[0])],texts[:1])
        self.assertIsNone(validate_brief(brief,early,texts[:1],'English'))
        self.assertIsNotNone(validate_brief(brief,early,texts[:1]+['What would you recommend?'],'English'))
        self.assertIsNone(validate_brief({**brief,'basis_quotes':['invented source']},a,texts,'English'))

    def test_wrong_epistemic_kind_cannot_make_unknowns_complete(self):
        a=apply_updates(empty_analysis(),[update('review','reviewer','I do not know who reviewed the file.')],['I do not know who reviewed the file.'])
        self.assertEqual(a['facts'][0]['kind'],'uncertain')
        self.assertEqual(dimension_states(a)['review']['coverage'],0)

class AnalysisExportTests(unittest.TestCase):
    def test_export_contains_coverage_sources_and_no_invented_facts(self):
        from inquiry.analysis import analysis_markdown
        from inquiry.review_packet import build_review_packet
        text='The CFO is my university classmate.'
        a=apply_updates(empty_analysis(),[update('interests','relationship',text)],[text])
        s=Session(messages=[{'role':'user','content':text},{'role':'assistant','content':'Who could review this?'},{'role':'user','content':'I do not yet know.'},{'role':'assistant','content':'Which records could identify a reviewer?'}],analysis=a)
        self.assertIn(a['facts'][0]['id'],s.export())
        self.assertIn('not a risk score',analysis_markdown(a,'English'))
        packet=build_review_packet(s)
        self.assertIn(a['facts'][0]['id'],packet)
        self.assertIn('Relationships',packet)

class ClassificationRobustnessTests(unittest.TestCase):
    def test_malformed_items_and_unclassified_input_do_not_force_a_dimension(self):
        text='I find the situation difficult to explain.'
        a=apply_updates(empty_analysis(),[None,{'area':{},'facet':[]},update('scope','unknown',text),update('pressure','wrong_facet',text)], [text])
        self.assertEqual(a['facts'],[])
        self.assertTrue(all(d['coverage']==0 for d in a['dimensions'].values()))

    def test_unanswered_facts_survive_a_legacy_question_without_invented_coverage(self):
        from inquiry.core import parse_turn
        previous=[{'area':'interests','quote':'The CFO is my university classmate.'}]
        _,_,quotes,a=parse_turn('{"question":"Which records could clarify this?","focus":"evidence"}',[previous[0]['quote']],empty_analysis(),'English',previous)
        self.assertEqual(quotes,previous)
        self.assertFalse(a['ready'])

    def test_curated_frontend_assets_match_the_same_backend_source(self):
        from pathlib import Path
        from inquiry.examples import EXAMPLES
        from inquiry.analysis import DEFINITIONS
        root=Path(__file__).resolve().parents[1]
        self.assertEqual(json.loads((root/'web/src/dimensions.json').read_text()),json.loads(json.dumps(DEFINITIONS)))
        self.assertEqual(json.loads((root/'web/src/cases.json').read_text()),[{**c,'analysis_en':seed_case(c,'English'),'analysis_zh':seed_case(c,'中文')} for c in EXAMPLES])

class ReviewRegressionTests(unittest.TestCase):
    def test_a_b_a_correction_has_current_source_and_no_retracted_active_claim(self):
        texts=['The CFO is my university classmate.','Correction: the CFO is not my classmate.','The CFO is my university classmate.']
        a=apply_updates(empty_analysis(),[update('interests','relationship',texts[0])],texts[:1])
        b=apply_updates(a,[update('interests','relationship',texts[1],2,replaces=[a['facts'][0]['id']])],texts[:2])
        c=apply_updates(b,[update('interests','relationship',texts[2],3,replaces=[b['facts'][1]['id']])],texts)
        active=[f for f in c['facts'] if f['status']=='active']
        self.assertEqual(len(active),1)
        self.assertEqual(active[0]['quote'],texts[2])
        self.assertEqual(active[0]['turn'],3)

    def test_sync_regeneration_preserves_legacy_quotes(self):
        class Client:
            def complete(self,messages):return '{"question":"Which original record could clarify the concern?","focus":"evidence"}',{}
        quote={'area':'interests','quote':'The CFO is my university classmate.'}
        s=Session(messages=[{'role':'user','content':quote['quote']},{'role':'assistant','content':'Who could review this?'}],observations=[quote])
        s.regenerate(Client())
        self.assertEqual(s.observations,[quote])

    def test_new_user_context_marks_unreassessed_brief_stale_even_if_updates_are_empty(self):
        from inquiry.core import parse_turn
        a=empty_analysis();a['brief']={'stale':False,'as_of_turn':1}
        raw='{"question":"Who could independently verify this?","focus":"review","analysis":{"updates":[]}}'
        _,_,_,same=parse_turn(raw,['Original situation.'],a,'English')
        self.assertFalse(same['brief']['stale'])
        _,_,_,new=parse_turn(raw,['Original situation.','The reviewer may also be involved in the problem.'],a,'English')
        self.assertTrue(new['brief']['stale'])

class CurrentUncertaintyTests(unittest.TestCase):
    def test_latest_unknown_reopens_a_previously_reported_facet_without_invented_retraction(self):
        texts=['An independent partner reviewed the file.','I cannot confirm who reviewed the file.','The quality partner confirmed reviewing it.']
        a=apply_updates(empty_analysis(),[update('review','reviewer',texts[0])],texts[:1])
        b=apply_updates(a,[update('review','reviewer',texts[1],2,'uncertain')],texts[:2])
        self.assertEqual(dimension_states(b)['review']['coverage'],0)
        c=apply_updates(b,[update('review','reviewer',texts[2],3)],texts)
        self.assertEqual(dimension_states(c)['review']['coverage'],1)
        d=apply_updates(c,[update('review','reviewer',texts[1],4,'uncertain')],texts+[texts[1]])
        self.assertEqual(dimension_states(d)['review']['coverage'],0)
