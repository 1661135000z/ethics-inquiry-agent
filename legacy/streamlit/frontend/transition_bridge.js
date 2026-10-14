export default function(component){
  const {data}=component;
  const anchors={model:'.model-summary',scenario:'.st-key-scenario_region',conversation:'.current-situation'};
  const selector=anchors[data.kind];if(!selector)return;
  const target=document.querySelector(selector)||document.querySelector('.st-key-model_entry');
  const regions=data.kind==='model'?['.st-key-scenario_region','.st-key-composer','.st-key-journey_rail']:['.st-key-transcript','.st-key-composer','.st-key-journey_rail'];
  getMotionRuntime().settle({nonce:data.nonce,kind:data.kind,title:data.title,zh:document.documentElement.lang?.startsWith('zh'),target,regions:regions.map(s=>document.querySelector(s))});
}
