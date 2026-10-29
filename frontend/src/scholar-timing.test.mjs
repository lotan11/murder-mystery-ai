import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {validateStudy,validateStudyAudio,studyPoseAt} from './scholar-timing.mjs';
const raw=JSON.parse(readFileSync(new URL('../public/character-lab/lewis-study.json',import.meta.url),'utf8'));
const audio=new Uint8Array(readFileSync(new URL('../public/character-lab/lewis-study.wav',import.meta.url)));

test('bundled Lewis audio, sample clock and timing metadata are paired',()=>{
 const manifest=validateStudy(raw);
 assert.equal(createHash('sha256').update(audio).digest('hex'),manifest.audio_sha256);
 assert.equal(validateStudyAudio(audio,manifest.duration_seconds),manifest.duration_seconds);
 assert.equal(manifest.playback_rate,1.05);
 assert.ok(manifest.phonemes.length>20);
});

test('mouth poses use source audio seconds and stay neutral in real gaps',()=>{
 const cues=[{phoneme:'a',start:.5,end:1},{phoneme:'u',start:1.2,end:1.6}];
 assert.equal(studyPoseAt(cues,.75).jawOpen,.24);
 assert.equal(studyPoseAt(cues,1.1).jawOpen,0);
 assert.equal(studyPoseAt(cues,1.4).mouthPucker,.18);
 assert.equal(studyPoseAt(cues,1.6).mouthPucker,0);
 assert.equal(studyPoseAt(cues,NaN).jawOpen,0);
});

test('unknown symbols and zero-duration markers never invent mouth motion',()=>{
 for(const phoneme of ['ˈ',' ','.','?']){
  const pose=studyPoseAt([{phoneme,start:0,end:1}],.5);
  assert.equal(pose.jawOpen+pose.lipPress+pose.mouthPucker+pose.mouthSmile,0);
 }
 assert.equal(studyPoseAt([{phoneme:'a',start:0,end:0}],0).jawOpen,0);
});

test('all recorded cues retain restrained motion and a soft onset',()=>{
 const manifest=validateStudy(raw);
 for(let t=0;t<manifest.duration_seconds;t+=.007){
  const pose=studyPoseAt(manifest.phonemes,t);
  assert.ok(pose.jawOpen>=0&&pose.jawOpen<=.38);
  assert.ok(pose.mouthPucker>=0&&pose.mouthPucker<=.25);
  assert.ok(pose.lipPress>=0&&pose.lipPress<=.25);
  assert.equal(pose.mouthSmile,0);
 }
 const cues=[{phoneme:'a',start:0,end:1}];
 assert.equal(studyPoseAt(cues,0).jawOpen,0);
 assert.ok(studyPoseAt(cues,.01).jawOpen<studyPoseAt(cues,.1).jawOpen);
});

test('unapproved voices, bad clocks and malformed cue boundaries are rejected',()=>{
 for(const change of [v=>v.voice='bm_george',v=>v.playback_rate=1.2,v=>v.phonemes[0].start=true,v=>v.phonemes[0].end=999,v=>v.phonemes[0].start=NaN,v=>v.phonemes=[],v=>v.phonemes[0].guessed=true]){
  const value=structuredClone(raw);change(value);assert.throws(()=>validateStudy(value));
 }
});

test('wrong or truncated waveform cannot silently drive this timing',()=>{
 assert.throws(()=>validateStudyAudio(audio.subarray(0,40),raw.duration_seconds));
 assert.throws(()=>validateStudyAudio(audio,raw.duration_seconds+1));
 const bad=audio.slice();bad[0]=0;assert.throws(()=>validateStudyAudio(bad,raw.duration_seconds));
});
