export type StudyCue = {phoneme:string;start:number;end:number};
export type StudyManifest = {schema_version:1;text:string;voice:'bm_lewis';generation_speed:number;playback_rate:number;duration_seconds:number;audio_sha256:string;timing_source:string;phonemes:StudyCue[]};
export type StudyPose = {jawOpen:number;mouthPucker:number;lipPress:number;mouthSmile:number;phoneme:string};
export function validateStudy(value:unknown):StudyManifest;
export function studyPoseAt(phonemes:StudyCue[],seconds:number):StudyPose;
export function validateStudyAudio(bytes:Uint8Array,duration:number):number;
