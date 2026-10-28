import asyncio, json, edge_tts, subprocess
VOICE="ko-KR-SunHiNeural"; RATE="+12%"
scenes=json.load(open("script.json"))
async def one(s):
    c=edge_tts.Communicate(s["text"],VOICE,rate=RATE,boundary="SentenceBoundary")
    subs=[]
    with open(f"assets/vo/{s['id']}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"].endswith("Boundary"):
                subs.append({"t":ch["offset"]/1e7,"d":ch["duration"]/1e7,"text":ch["text"]})
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"assets/vo/{s['id']}.mp3"]))
    return {"id":s["id"],"dur":dur,"subs":subs}
async def main():
    out=[await one(s) for s in scenes]
    json.dump(out,open("vo.json","w"),ensure_ascii=False,indent=1)
    for o in out: print(o["id"],round(o["dur"],2),len(o["subs"]))
    print("total",round(sum(o["dur"] for o in out),2))
asyncio.run(main())
