export function validateStudy(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || value.schema_version !== 1 || value.voice !== 'bm_lewis' || value.generation_speed !== .92 || value.playback_rate !== 1.05 || value.timing_source !== 'kokoro-model-duration') throw Error('The local Lewis study metadata is invalid.');
  if (typeof value.text !== 'string' || !value.text.trim() || value.text.length > 1500 || !Number.isFinite(value.duration_seconds) || value.duration_seconds < .1 || value.duration_seconds > 170 || !/^[a-f0-9]{64}$/.test(value.audio_sha256 || '')) throw Error('The local Lewis study metadata is invalid.');
  if (!Array.isArray(value.phonemes) || !value.phonemes.length || value.phonemes.length > 4000) throw Error('The local Lewis study has no bounded phoneme timing.');
  let previous = 0;
  const phonemes = value.phonemes.map(cue => {
    if (!cue || typeof cue !== 'object' || Object.keys(cue).sort().join(',') !== 'end,phoneme,start' || typeof cue.phoneme !== 'string' || !cue.phoneme.length || cue.phoneme.length > 8 || /[\u0000-\u001f\u007f]/.test(cue.phoneme) || !Number.isFinite(cue.start) || !Number.isFinite(cue.end) || cue.start < previous - 1e-6 || cue.start < 0 || cue.end < cue.start || cue.end > value.duration_seconds + 1e-6) throw Error('The local Lewis study timing is invalid.');
    previous = cue.end;
    return {phoneme: cue.phoneme, start: cue.start, end: cue.end};
  });
  return {...value, phonemes};
}

export function studyPoseAt(phonemes, seconds) {
  const neutral = {jawOpen: 0, mouthPucker: 0, lipPress: 0, mouthSmile: 0, phoneme: ''};
  if (!Number.isFinite(seconds) || seconds < 0) return neutral;
  const cue = phonemes.find(c => c.start <= seconds && seconds < c.end && c.end > c.start);
  if (!cue) return neutral;
  const symbol = cue.phoneme;
  let jawOpen = 0, mouthPucker = 0, lipPress = 0;
  if (/^[pbm]$/.test(symbol)) lipPress = .20;
  else if (/^[oɔʊuwɒ]$/.test(symbol)) {jawOpen = .10; mouthPucker = .18;}
  else if (/^[aɑæʌɐ]$/.test(symbol)) jawOpen = .24;
  else if (/^[eɛɜiɪəɚɨʉɝ]$/.test(symbol)) jawOpen = .14;
  else if (/^[tdkgfvszʃʒθðnlɹrjŋɡʧʤhɾ]$/.test(symbol)) jawOpen = .05;
  const ramp = Math.min(.03, (cue.end - cue.start) * .3);
  const envelope = ramp > 0 ? Math.max(0, Math.min(1, (seconds-cue.start)/ramp, (cue.end-seconds)/ramp)) : 0;
  return {jawOpen: jawOpen*envelope, mouthPucker: mouthPucker*envelope, lipPress: lipPress*envelope, mouthSmile: 0, phoneme: symbol};
}
export function validateStudyAudio(bytes, duration) {
  if (!(bytes instanceof Uint8Array) || bytes.byteLength < 44 || bytes.byteLength > 8*1024*1024) throw Error('The fixed local study audio is invalid.');
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  if (view.getUint32(0, false) !== 0x52494646 || view.getUint32(8, false) !== 0x57415645 || view.getUint32(4,true) !== bytes.byteLength-8) throw Error('The fixed local study WAV header is invalid.');
  let offset=12, format=false, frames=0, foundData=false;
  while (offset+8<=bytes.byteLength) {
    const kind=view.getUint32(offset,false), size=view.getUint32(offset+4,true);offset+=8;
    if (offset+size>bytes.byteLength) throw Error('The fixed local study WAV is truncated.');
    if (kind===0x666d7420) {
      if (format || size<16 || view.getUint16(offset,true)!==1 || view.getUint16(offset+2,true)!==1 || view.getUint32(offset+4,true)!==24000 || view.getUint16(offset+12,true)!==2 || view.getUint16(offset+14,true)!==16) throw Error('The fixed local study WAV format is unsupported.');
      format=true;
    }
    if (kind===0x64617461) {if(foundData || size%2)throw Error('The fixed local study WAV data is invalid.');foundData=true;frames=size/2;}
    offset+=size+(size%2);
  }
  if (!format || !foundData || offset!==bytes.byteLength || frames<2400 || frames>24000*170 || Math.abs(frames/24000-duration)>.001) throw Error('The fixed local study duration does not match its timing.');
  return frames/24000;
}
