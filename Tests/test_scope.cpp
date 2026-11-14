// Runs the real engine + ScopeBuffer on the test signals at 175 BPM, dumps the buffer for plotting.
#include "../Source/PhaseAlignCore.h"
#include "../Source/ScopeBuffer.h"
#include <cstdio>
#include <vector>
static std::vector<float> rd (const char* f){ FILE* fp=fopen(f,"rb"); fseek(fp,0,SEEK_END); long n=ftell(fp)/4; fseek(fp,0,SEEK_SET); std::vector<float> v((size_t)n); if(fread(v.data(),4,(size_t)n,fp)!=(size_t)n) return {}; fclose(fp); return v; }
int main(int argc,char**argv){
  const double fs=44100, bpm=175; psy::PhaseAligner a; a.prepare(fs); psy::Params p; p.groupMode=false; p.targetDeg = argc>1? (float)atof(argv[1]):0.f;
  auto K=rd("/tmp/kick.f32"), B=rd("/tmp/bass.f32"); size_t n=std::min(K.size(),B.size());
  static psy::ScopeBuffer sb; const int blk=512; std::vector<float> tk(blk),tbi(blk),tbo(blk);
  double ppq=0.0, pps=bpm/(60.0*fs); double maxdiff=0;
  std::vector<float> outAll; 
  for(size_t pos=0; pos+blk<=n; pos+=blk){
    std::vector<float> l(B.begin()+pos,B.begin()+pos+blk), r=l, kl(K.begin()+pos,K.begin()+pos+blk), kr=kl;
    float* m[2]={l.data(),r.data()}; const float* k[2]={kl.data(),kr.data()};
    psy::PhaseAligner::Tap tap{tk.data(),tbi.data(),tbo.data()};
    a.process(m,2,k,2,blk,p,&tap);
    for(int i=0;i<blk;++i) maxdiff=std::max(maxdiff,(double)std::abs(tbo[i]-l[i]));   // track mode: bassOut must equal the output
    sb.write(ppq - a.getLatencySamples()*pps, pps, blk, tk.data(), tbi.data(), tbo.data());
    ppq += blk*pps;
  }
  printf("tap bassOut vs output max diff: %.2e\n", maxdiff);
  FILE* o=fopen("/tmp/scope.bin","wb"); int cur=sb.currentSlice(); fwrite(&cur,4,1,o);
  for(int s=0;s<psy::ScopeBuffer::kSlices;++s) for(int g=0;g<3;++g) for(int c=0;c<psy::ScopeBuffer::kCols;++c){ float mn=sb.get(s,g,c,0), mx=sb.get(s,g,c,1); fwrite(&mn,4,1,o); fwrite(&mx,4,1,o);} fclose(o);
}
