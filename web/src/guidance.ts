export const GUIDE_KEY='inquire.guide.v1';
export function shouldIntroduceGuide(s:{screen:string;verified:boolean;ready:boolean;busy:boolean;seen:boolean;hasMessages:boolean;sheetOpen:boolean;draftStarted:boolean;editing?:boolean;settingsOpen?:boolean}){
 return s.screen==='cases'&&s.verified&&s.ready&&!s.busy&&!s.seen&&!s.hasMessages&&!s.sheetOpen&&!s.draftStarted&&!s.editing&&!s.settingsOpen;
}
export function composerHeight(scrollHeight:number,screen:string){
 const min=screen==='cases'?128:88,max=screen==='cases'?240:192;
 return {height:Math.max(min,Math.min(max,scrollHeight)),scroll:scrollHeight>max};
}
