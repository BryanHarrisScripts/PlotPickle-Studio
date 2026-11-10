#!/usr/bin/env python3
"""Offline, no-generation acceptance tests for PlotPickle production design."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

script=Path(__file__).with_name("design-review.py")
spec=importlib.util.spec_from_file_location("plotpickle_design_review",script)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture(kind="character"):
    ids=m.CHAR_IDS if kind=="character" else m.WORLD_IDS
    text="MARA opens a gate." if kind=="character" else "EXT. GARDEN - DAY"
    pass_id="p-3" if kind=="character" else "p-1"
    project={"id":"story-1","revision":3,"sha256":"a"*64}
    subject={"id":"mara","name":"Mara"} if kind=="character" else {"id":"garden","name":"EXT. GARDEN - DAY"}
    panels=[{"id":x,"title":x.upper(),"promptGuidance":"Preserve source continuity.",
             "image":None,"imageVerified":False,"visualApproval":"pending"} for x in ids]
    layout={"schema":"plotpickle.design-layout.v1","status":"empty-template","kind":kind,
            "project":project,"subject":subject,"sourceEvidenceIds":[pass_id],
            "columns":3 if kind=="character" else 2,"rows":3,
            "cellAspectRatio":"1:1" if kind=="character" else "16:9",
            "panels":panels,"mediaGenerated":False,"projectModified":False,"designApproved":False}
    brief={"schema":"plotpickle.design-brief.v1","status":"draft-proposal","kind":kind,
           "project":project,"subject":subject,"mediaGenerated":False,"projectModified":False,
           "sourceEvidence":[{"passageId":pass_id,"type":"action" if kind=="character" else "scene-heading",
                              "text":text,"textSha256":hashlib.sha256(text.encode()).hexdigest()}]}
    return layout,brief

def png(w,h):
    # Header-valid only; production-design always reports pixelsDecoded=False.
    return b"\x89PNG\r\n\x1a\n"+struct.pack(">I",13)+b"IHDR"+struct.pack(">II",w,h)+b"\x08\x06\x00\x00\x00"+b"\x00\x00\x00\x00"

def webp_vp8x(w,h):
    payload=b"\x00\x00\x00\x00"+(w-1).to_bytes(3,"little")+(h-1).to_bytes(3,"little")
    chunk=b"VP8X"+len(payload).to_bytes(4,"little")+payload
    return b"RIFF"+(4+len(chunk)).to_bytes(4,"little")+b"WEBP"+chunk

class DesignProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.layout,self.brief=fixture()
    def tearDown(self):self.temp.cleanup()
    def write(self,name,data):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return p
    def test_prompt_pack_is_nine_square_not_generated(self):
        v=m.prompt_pack(self.layout,self.brief)
        self.assertEqual(len(v["panels"]),9)
        self.assertTrue(all(p["aspectRatio"]=="1:1" and p["status"]=="prompt-only-no-image" for p in v["panels"]))
        self.assertFalse(v["imagesGenerated"]);self.assertFalse(v["designApproved"])
        self.assertIn("untrusted story DATA",v["promptSafety"])
    def test_world_has_six_landscape_prompts(self):
        l,b=fixture("world");out=m.prompt_pack(l,b)
        self.assertEqual(len(out["panels"]),6)
        self.assertTrue(all(p["aspectRatio"]=="16:9" for p in out["panels"]))
    def test_prompt_rejects_cross_story_source_and_hash_tampering(self):
        b=copy.deepcopy(self.brief);b["project"]["revision"]=4
        with self.assertRaisesRegex(ValueError,"source or subject mismatch"):m.prompt_pack(self.layout,b)
        b=copy.deepcopy(self.brief);b["sourceEvidence"][0]["text"]="Unexpected revision"
        with self.assertRaisesRegex(ValueError,"hash mismatch"):m.prompt_pack(self.layout,b)
    def test_long_passage_uses_excerpt_hash_without_claiming_full_text_verification(self):
        b=copy.deepcopy(self.brief)
        full="A very long descriptive screenplay passage. "*20
        short=full[:540]
        e=b["sourceEvidence"][0]
        e.update({"text":short,
                  "textSha256":hashlib.sha256(full.encode()).hexdigest(),
                  "excerptSha256":hashlib.sha256(short.encode()).hexdigest(),
                  "excerptTruncated":True})
        pack=m.prompt_pack(self.layout,b)
        self.assertTrue(pack["sourcePassages"][0]["excerptTruncated"])
        tampered=copy.deepcopy(b);tampered["sourceEvidence"][0]["text"]="X"+short[1:]
        with self.assertRaisesRegex(ValueError,"excerpt hash"):
            m.prompt_pack(self.layout,tampered)
        legacy=copy.deepcopy(b);legacy["sourceEvidence"][0].pop("excerptSha256")
        with self.assertRaisesRegex(ValueError,"Legacy passage excerpt"):
            m.prompt_pack(self.layout,legacy)
    def test_exact_image_hash_and_header_staging(self):
        raw=png(1024,1024);self.write("design/face.png",raw)
        c=m.stage(self.layout,"face",self.root,"design/face.png")
        self.assertEqual(c["media"]["sha256"],hashlib.sha256(raw).hexdigest())
        self.assertEqual(c["media"]["width"],1024)
        self.assertFalse(c["media"]["pixelsDecoded"])
        self.assertEqual(c["authorApproval"],"not-recorded")
        self.assertFalse(c["ppfSaved"]);self.assertFalse(c["ppfLocked"])
    def test_webp_vp8x_header(self):
        l,_=fixture("world"); self.write("loc.webp",webp_vp8x(1920,1080))
        c=m.stage(l,"establishing",self.root,"loc.webp")
        self.assertEqual(c["media"]["mimeType"],"image/webp")
        self.assertEqual([c["media"]["width"],c["media"]["height"]],[1920,1080])
    def test_reject_malformed_webp_length(self):
        raw=webp_vp8x(1024,1024)+b"x";self.write("bad.webp",raw)
        with self.assertRaisesRegex(ValueError,"RIFF"):m.stage(self.layout,"face",self.root,"bad.webp")
    def test_wrong_aspect_and_unknown_panel_rejected(self):
        self.write("w.png",png(1920,1080))
        with self.assertRaisesRegex(ValueError,"aspect ratio"):m.stage(self.layout,"face",self.root,"w.png")
        with self.assertRaisesRegex(ValueError,"Unknown layout panel"):m.stage(self.layout,"side-angle",self.root,"w.png")
    def test_unsafe_paths_and_symlink_escape_rejected(self):
        self.write("ok.png",png(512,512))
        for path in ("../ok.png","/etc/passwd","C:/temp/ok.png","a\\file.png"):
            with self.subTest(path=path),self.assertRaisesRegex(ValueError,"Unsafe"):m.stage(self.layout,"face",self.root,path)
        with tempfile.TemporaryDirectory() as other:
            out=Path(other)/"foo.png";out.write_bytes(png(512,512))
            (self.root/"link.png").symlink_to(out)
            with self.assertRaisesRegex(ValueError,"escapes assets root"):m.stage(self.layout,"face",self.root,"link.png")
    def test_review_partial_truth(self):
        self.write("face.png",png(512,512));c=m.stage(self.layout,"face",self.root,"face.png")
        r=m.review(self.layout,[c],self.root)
        self.assertEqual(r["verifiedCandidateCount"],1)
        self.assertEqual(len(r["missingPanelIds"]),8)
        self.assertFalse(r["readyForAuthorReview"]);self.assertFalse(r["designApproved"])
    def test_review_rechecks_bytes_and_revision(self):
        self.write("face.png",png(512,512));c=m.stage(self.layout,"face",self.root,"face.png")
        self.write("face.png",png(1024,1024))
        with self.assertRaisesRegex(ValueError,"changed after receipt"):m.review(self.layout,[c],self.root)
        c=m.stage(self.layout,"face",self.root,"face.png")
        l=copy.deepcopy(self.layout);l["project"]["revision"]=4
        with self.assertRaisesRegex(ValueError,"source/subject/revision mismatch"):m.review(l,[c],self.root)
    def test_review_rejects_forged_approval_and_duplicate_panel(self):
        self.write("face.png",png(512,512));c=m.stage(self.layout,"face",self.root,"face.png")
        bad=copy.deepcopy(c);bad["authorApproval"]="approved"
        with self.assertRaisesRegex(ValueError,"unsupported approval"):m.review(self.layout,[bad],self.root)
        with self.assertRaisesRegex(ValueError,"duplicate panel"):m.review(self.layout,[c,c],self.root)
    def test_full_unique_sheet_ready_for_review_not_canon(self):
        cs=[]
        for i,pid in enumerate(m.CHAR_IDS):
            name=f"{pid}.png"
            self.write(name,png(512+i,512+i))
            cs.append(m.stage(self.layout,pid,self.root,name))
        r=m.review(self.layout,cs,self.root)
        self.assertTrue(r["readyForAuthorReview"])
        self.assertEqual(r["missingPanelIds"],[])
        self.assertFalse(r["designApproved"]);self.assertFalse(r["ppfSaved"])
    def test_duplicate_hash_blocks_review_readiness(self):
        cs=[]
        self.write("same.png",png(512,512))
        for pid in m.CHAR_IDS:cs.append(m.stage(self.layout,pid,self.root,"same.png"))
        r=m.review(self.layout,cs,self.root)
        self.assertFalse(r["readyForAuthorReview"])
        self.assertEqual(len(r["duplicateImageHashPanels"][0]),9)
    def test_no_overwrite(self):
        path=self.root/"candidate.json"
        m.save_new(path,{"candidate":"one"})
        with self.assertRaises(FileExistsError):m.save_new(path,{"candidate":"two"})
        self.assertEqual(json.loads(path.read_text())["candidate"],"one")
    def test_layout_cannot_claim_approved(self):
        l=copy.deepcopy(self.layout);l["designApproved"]=True
        with self.assertRaisesRegex(ValueError,"empty source-bound layouts"):m.validate_layout(l)

if __name__=="__main__":unittest.main(verbosity=2)
