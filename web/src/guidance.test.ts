import {it,expect} from 'vitest';
import {shouldIntroduceGuide,composerHeight} from './guidance';
it('introduces the existing guide only at a quiet first situation entry',()=>{
 const entry={screen:'cases',verified:true,ready:true,busy:false,seen:false,hasMessages:false,sheetOpen:false,draftStarted:false};
 expect(shouldIntroduceGuide(entry)).toBe(true);
 for(const change of [{busy:true},{seen:true},{hasMessages:true},{sheetOpen:true},{draftStarted:true},{ready:false},{verified:false},{screen:'welcome'},{screen:'chat'},{editing:true},{settingsOpen:true}])expect(shouldIntroduceGuide({...entry,...change})).toBe(false);
});
it('keeps the contextual composer within bounded usable heights',()=>{
 expect(composerHeight(40,'chat')).toEqual({height:88,scroll:false});
 expect(composerHeight(400,'chat')).toEqual({height:192,scroll:true});
 expect(composerHeight(180,'cases')).toEqual({height:180,scroll:false});
});
