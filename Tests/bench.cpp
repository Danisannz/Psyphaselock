#include "../Source/PhaseAlignCore.h"
#include <chrono>
#include <cstdio>
#include <vector>
int main(){
  const double fs=48000; const int block=64; const int secs=60; psy::PhaseAligner a; a.prepare(fs);
  psy::Params p; std::vector<float> l(block),r(block),kl(block),kr(block);
  uint32_t s=1; auto rnd=[&]{ s=s*1664525u+1013904223u; return (float)(s>>8)/16777216.f-0.5f; };
  auto t0=std::chrono::steady_clock::now();
  for(long b=0;b<(long)(fs*secs/block);++b){
    for(int i=0;i<block;++i){ float t=(float)((b*block+i)/fs); l[i]=r[i]=0.4f*std::sin(6.2831853f*55*t)+0.05f*rnd(); kl[i]=kr[i]=0.3f*std::sin(6.2831853f*55*t+1)*(float)(std::fmod(t,0.343)<0.2); }
    float* m[2]={l.data(),r.data()}; const float* k[2]={kl.data(),kr.data()}; a.process(m,2,k,2,block,p);
  }
  double el=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
  printf("%d s of stereo audio @48k, block %d processed in %.3f s -> %.2f%% of ONE core (%.1fx realtime)\n",secs,block,el,100.0*el/secs,secs/el);
}
