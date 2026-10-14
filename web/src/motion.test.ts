import {beforeEach,afterEach,it,expect,vi} from 'vitest';
import gsap from 'gsap';
import {morph} from './motion';
vi.mock('gsap',()=>({default:{registerPlugin:vi.fn(),set:vi.fn(),timeline:vi.fn()}}));
vi.mock('gsap/Flip',()=>({default:{fit:vi.fn()}}));
const remove=vi.fn();
function element(){return {classList:{add:vi.fn()},removeAttribute:vi.fn(),setAttribute:vi.fn(),querySelectorAll:()=>[],style:{removeProperty:vi.fn()},remove,inert:false,innerHTML:''}}
beforeEach(()=>{vi.clearAllMocks();vi.stubGlobal('getComputedStyle',()=>({fontFamily:'sans-serif',fontSize:'14px'}));vi.stubGlobal('window',{matchMedia:()=>({matches:false}),scrollTo:vi.fn(),setTimeout,clearTimeout});vi.stubGlobal('document',{documentElement:{dataset:{}},createElement:element,querySelectorAll:()=>[],body:{append:vi.fn()}})});
afterEach(()=>vi.unstubAllGlobals());
const source=()=>({dataset:{model:'gemini'},getBoundingClientRect:()=>({left:10,top:10,width:200,height:100}),cloneNode:element}) as unknown as HTMLElement;
it('commits and releases the transition even when GSAP timeline creation fails',async()=>{
 vi.mocked(gsap.timeline).mockImplementation(()=>{throw new Error('animation unavailable')});const update=vi.fn();
 await expect(morph(source(),()=>null,update)).resolves.toBeUndefined();expect(update).toHaveBeenCalledOnce();expect(document.documentElement.dataset.transiting).toBeUndefined();expect(remove).toHaveBeenCalledTimes(2);
});
it('does not strand accepted state when an animation setup call throws',async()=>{
 vi.mocked(gsap.timeline).mockReturnValue({kill:vi.fn()} as never);vi.mocked(gsap.set).mockImplementation(()=>{throw new Error('set failed')});const update=vi.fn();
 await expect(morph(source(),()=>null,update)).resolves.toBeUndefined();expect(update).toHaveBeenCalledOnce();expect(remove).toHaveBeenCalledTimes(2);
});
