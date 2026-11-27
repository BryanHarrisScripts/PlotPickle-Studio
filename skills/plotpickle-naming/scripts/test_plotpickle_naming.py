import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from plotpickle_naming import basename,reconcile

def test():
    assert basename("Afterglow",3,4,2,1,"image/png")=="AFTERGLOW_B03_MB04_S02_V001.png"
    assert basename("The Third Bell",1,1,25,2,"webp")=="THE_THIRD_BELL_B01_MB01_S25_V002.webp"
    try:
        basename("A",0,1,1,1,"png")
        raise AssertionError("invalid block accepted")
    except ValueError: pass
    with TemporaryDirectory() as td:
        root=Path(td); src=root/"source"; dst=root/"dest"; src.mkdir(); dst.mkdir()
        payload=b"Test only, not an image file"; (src/"legacy.bin").write_bytes(payload)
        sha=hashlib.sha256(payload).hexdigest()
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps([{"project":"Afterglow","block":1,"miniBlock":1,"shot":1,"version":1,"extension":"png","source":"legacy.bin","sha256":sha,"bytes":len(payload)}]))
        check=reconcile(manifest,src,dst)
        assert check["records"][0]["state"]=="COPY_PENDING"
        assert not list(dst.iterdir())
        result=reconcile(manifest,src,dst,True)
        assert result["copiesVerified"]==1
        assert (src/"legacy.bin").read_bytes()==payload
        assert reconcile(manifest,src,dst,True)["copiesVerified"]==1
        (dst/"AFTERGLOW_B01_MB01_S01_V001.png").write_bytes(b"different")
        assert reconcile(manifest,src,dst,True)["records"][0]["state"]=="DESTINATION_COLLISION"
        assert (src/"legacy.bin").read_bytes()==payload
if __name__=="__main__": test(); print("Naming V1 tests PASS")
