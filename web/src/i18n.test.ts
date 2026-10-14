import {describe,it,expect} from 'vitest';
import {localizeMessage,cachedRecord} from './i18n';
describe('interface localization',()=>{
 it('renders stored provider errors in the current language and preserves HTTP status',()=>{
  const raw='Gemini 不接受当前请求来源的地区，请切换 GLM；这不是访问码错误。（HTTP 400）';
  const english=localizeMessage(raw,'English');
  expect(english).toContain('region');expect(english).toContain('HTTP 400');expect(english).not.toMatch(/\p{Script=Han}/u);
  expect(localizeMessage(raw,'中文')).toBe(raw);
 });
 it('translates recovery, quota and mirror errors without losing their purpose',()=>{
  for(const raw of ['会话已过期，请开始新的探究。','免费额度或服务容量不足，请稍后再试或手动切换。（HTTP 429）','镜像暂时无法连接后端，请稍后重试。']){
   expect(localizeMessage(raw,'English')).not.toMatch(/\p{Script=Han}/u);
  }
  expect(localizeMessage('复制不可用，请选中文字复制。','English')).toMatch(/copy/i);
 });
 it('localizes cached export labels while preserving original statements and draft',()=>{
  const record=cachedRecord([{role:'user',content:'用户原话不应被翻译'}],'未发送原话','English');
  expect(record).toContain('Cached inquiry');expect(record).toContain('Unsent draft');
  expect(record).toContain('用户原话不应被翻译');expect(record).toContain('未发送原话');
  expect(record).not.toContain('后台会话不可用');
 });
});
