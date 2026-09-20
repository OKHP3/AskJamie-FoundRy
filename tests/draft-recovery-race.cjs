const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../workbench/static/app.js'), 'utf8');
const load = source.slice(source.indexOf('  async function loadProject('), source.indexOf('  function projectSwitchLabel'));
const restore = source.slice(source.indexOf('  async function restoreLocalDraft('), source.indexOf('  function reconcileLocalRevisionMismatch'));
const make = () => {
  const pending = new Map();
  const state = {projects: [{id:'a'}, {id:'b'}], current:null, projectLoadToken:0,
    localDrafts:{a:{draft:{title:'private A draft'},baseRevision:1}}};
  const context = {state, canLeaveCurrent:()=>true, render:()=>{}, announce:()=>{},
    api:(url)=>new Promise((resolve,reject)=>pending.set(url,{resolve,reject}))};
  vm.createContext(context); vm.runInContext(load + restore,context);
  const finish = async (id) => {
    pending.get('/api/projects/'+id).resolve({id,title:'saved '+id,revision:1});
    await new Promise(setImmediate);
    pending.get('/api/projects/'+id+'/history').resolve({history:[]});
    pending.get('/api/projects/'+id+'/evaluations').resolve({evaluations:[]});
    await new Promise(setImmediate);
  };
  return {context,state,pending,finish};
};
(async()=>{
  const a=make(); const restore=a.context.restoreLocalDraft('a');
  const switchToB=a.context.loadProject('b',true);
  await a.finish('b'); await switchToB;
  await a.finish('a'); await restore;
  assert.equal(a.state.current.id,'b'); assert.equal(a.state.current.title,'saved b');
  assert.equal(a.state.current._dirty,undefined);
  const b=make(); const recovery=b.context.restoreLocalDraft('a'); await b.finish('a'); await recovery;
  assert.equal(b.state.current.id,'a'); assert.equal(b.state.current.title,'private A draft');
  assert.equal(b.state.current._dirty,true);
  const c=make(); c.state.current={id:'b',title:'saved b'};
  const failed=c.context.restoreLocalDraft('a'); c.pending.get('/api/projects/a').reject(new Error('offline')); await failed;
  assert.equal(c.state.current.title,'saved b'); assert.equal(c.state.current._dirty,undefined);
  console.log('Recovery interleaving, successful recovery, and failed-load isolation passed.');
})().catch(e=>{console.error(e);process.exitCode=1;});
